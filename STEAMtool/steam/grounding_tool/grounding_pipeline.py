import os
from pathlib import Path
import pickle
import torch
import librosa
import fire
import librosa
import re
from steam.grounding_tool.grounding_utils import train_util, eval_util
from steam.grounding_tool.grounding_utils.build_vocab import Vocabulary

def get_grounding_model(experiment_path="grounding_ckpt"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device)

    exp_dir = Path(experiment_path)
    config = train_util.parse_config_or_kwargs(exp_dir / "config.yaml")

    model = train_util.init_obj_from_str(
        config["model"],
    )
    ckpt = torch.load(exp_dir / "best.pth", "cpu")
    train_util.load_pretrained_model(model, ckpt, output_fn=print_pass)
    model = model.to(device)
    
    vocabulary = Vocabulary()
    vocabulary.load_state_dict(pickle.load(open(Path(exp_dir / "vocab_state_dict.pkl"), "rb")))
    model.vocabulary = vocabulary
    model.device = device
    return model

def print_pass(*args):
    pass

def grounding_inference(
    model,
    audio_file=None,
    waveform=None,
    waveform_sample=None,
    phrase=None,     
    threshold=0.5,
    sample_rate=32000,
    window_size=1,
    continue_window=0.2):

    if audio_file == None:
        assert waveform_sample != None
        if waveform_sample != sample_rate:
            waveform = librosa.core.resample(waveform, orig_sr=waveform_sample, target_sr=sample_rate)
    else:
        waveform, _ = librosa.core.load(audio_file, sr=sample_rate)
    duration = waveform.shape[0] / sample_rate
    phrase = re.sub(r'[^\w\s]', '', phrase.lower())
    text = [model.vocabulary(token) for token in phrase.split()]

    input_dict = {
        "waveform": torch.as_tensor(waveform).unsqueeze(0).to(model.device),
        "waveform_len": [len(waveform)],
        "text": torch.as_tensor(text).long().reshape(1, 1, -1).to(model.device),
        "text_len": torch.tensor(len(text)).reshape(1, 1),
        "specaug": False
    }

    model.eval()
    with torch.no_grad():
        model_output = model(input_dict)
    prob = model_output["frame_sim"][0, :, 0].cpu().numpy()

    filtered_prob = eval_util.median_filter(prob[None, :], window_size=window_size, threshold=threshold)[0]
    change_indices = eval_util.find_contiguous_regions(filtered_prob)
    time_resolution = model.audio_encoder.time_resolution
    
    results = []

    # fix ratio
    ratio = 32000 / sample_rate
    last_offset = -1
    for row in change_indices:
        onset = round(row[0] * time_resolution * ratio, 2)
        offset = round(row[1] * time_resolution * ratio, 2)
        if (onset - last_offset) < continue_window:
            results[-1][-1] = offset
        else:
            results.append([onset, offset])
        last_offset = offset

    return results
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Inference for text to audio generation task.")
    parser.add_argument(
        "--audio_path", "-p", type=str, default="",
        help="",
    )
    parser.add_argument(
        "--text", "-t", type=str, default="Train",
        help="",
    )  
    parser.add_argument(
        "--th", "-th", type=float, default=0.5,
        help="",
    )  
    parser.add_argument(
        "--ws", "-ws", type=int, default=1,
        help="",
    )  
    args = parser.parse_args()
    model = get_grounding_model(experiment_path="steam/grounding_tool/grounding_ckpt")
    result = grounding_inference(model=model,
                                audio_file=args.audio_path,
                                phrase=args.text.lower(),
                                threshold=args.th,
                                window_size=args.ws,
        )
    audio, sr = librosa.load(args.audio_path, sr=16000)
    print(sr)
    result = grounding_inference(model=model,
                                audio_file=None,
                                waveform=audio,
                                waveform_sample=sr,
                                phrase=args.text.lower(),
                                threshold=args.th,
                                window_size=args.ws,
        )
    print(result)
    
    
    

   

