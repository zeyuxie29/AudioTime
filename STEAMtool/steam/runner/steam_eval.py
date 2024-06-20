import os
import copy
import json
import numpy as np
import torch
import argparse
import librosa
import sed_eval
import dcase_util
from tqdm import tqdm 
from pathlib import Path

from steam.grounding_tool.grounding_pipeline import grounding_inference, get_grounding_model

def calculate_sed_metric(ref_list, pred_list, time_resulution=1.0):
    reference_event_list = dcase_util.containers.MetaDataContainer(ref_list)
    estimated_event_list = dcase_util.containers.MetaDataContainer(pred_list)

    segment_based_metrics = sed_eval.sound_event.SegmentBasedMetrics(
        event_label_list=reference_event_list.unique_event_labels,
        time_resolution=time_resulution
    )
    event_based_metrics = sed_eval.sound_event.EventBasedMetrics(
        event_label_list=reference_event_list.unique_event_labels,
        t_collar=0.250
    )

    for filename in reference_event_list.unique_files:
        reference_event_list_for_current_file = reference_event_list.filter(
            filename=filename
        )

        estimated_event_list_for_current_file = estimated_event_list.filter(
            filename=filename
        )

        segment_based_metrics.evaluate(
            reference_event_list=reference_event_list_for_current_file,
            estimated_event_list=estimated_event_list_for_current_file
        )
        event_based_metrics.evaluate(
            reference_event_list=reference_event_list_for_current_file,
            estimated_event_list=estimated_event_list_for_current_file
        )

    # Get only certain metrics
    output = {
        "Segment_based Result": segment_based_metrics.results_overall_metrics(),
        "Event_based Result": event_based_metrics.results_overall_metrics()
    }
    print("#### Segment F1:", segment_based_metrics.results_overall_metrics()['f_measure']['f_measure'])
    return output


def get_grounding_result(args):
    pred_list, refs_list, pred_dict = [], [], {}
    refs_dict = json.load(open(args.test_json_path, "r"))
    grounding_model = get_grounding_model(experiment_path=args.grounding_ckpt_path)

    for file, item in tqdm(refs_dict.items()): 
        audio_path = Path(args.generated_path) / f"{file}.wav"
        pred_dict[file] = {"event": {}, "whole_event": {}}  

        for event, event_onset_list in item['event'].items():
            pred_dict[file]['event'][event] = []
            if args.task_name == "timestamp":
                for start, end in event_onset_list:
                    refs_list.append({
                        'event_label': event,
                        'onset': start,
                        'offset': end,
                        'filename': file,
                    }) 
            onset_result = grounding_inference(model=grounding_model,
                                audio_file=audio_path,
                                phrase=event,
                                threshold=0.4)

            pred_event_start, pred_event_end = 10, 0        
            for start_end in onset_result:
                if args.task_name == "timestamp":
                    pred_list.append({
                        'event_label': event,
                        'onset': start_end[0],
                        'offset': start_end[1],
                        'filename': file,
                    })  
                pred_dict[file]['event'][event].append(start_end)
                pred_event_start = min(pred_event_start, start_end[0])
                pred_event_end = max(pred_event_end, start_end[1])
            if pred_event_start < pred_event_end:
                pred_dict[file]['whole_event'][event] = (pred_event_start, pred_event_end, pred_event_end - pred_event_start)

    return {
            "pred_list": pred_list, 
            "refs_list": refs_list,
            "pred_dict": pred_dict,
            "refs_dict": refs_dict,}

def calculate_duration_error(grounding_result):
    refs_dict, pred_dict = grounding_result['refs_dict'], grounding_result['pred_dict']
    total_error, total_test_num, non_detect =  0, 0, 0

    for file, item in tqdm(refs_dict.items()): 
        pred_dict[file]["error"] = {}
        pred_dict[file]["refs_event"] = item['event']
        for event, event_duration_list in item['event'].items():
            total_test_num += 1         
            assert len(event_duration_list) == 1, "The duration evaluation necessitates ensuring that the reference event occurs only once."
            
            if len(pred_dict[file]['event'][event]) == 0: # No events were detected by grounding model
                pred_dict[file]["error"][event] = event_duration_list[0]
                non_detect += 1
            else:
                pred_dict[file]["error"][event] = abs(event_duration_list[0] - (pred_dict[file]["whole_event"][event][2]))
            total_error += pred_dict[file]["error"][event]
    
    print("#### Duration absolute error second/event:", round(total_error / total_test_num, 3))
    return pred_dict

def calculate_frequency_error(grounding_result):
    refs_dict, pred_dict = grounding_result['refs_dict'], grounding_result['pred_dict']
    total_error, total_test_num, confusion_matrix = 0, 0, np.zeros((10, 10))
     
    for file, item in tqdm(refs_dict.items()): 
        pred_dict[file]["error"] = {}
        pred_dict[file]["refs_event"] = item['event']
        for event, event_info_list in item['event'].items():
            total_test_num += 1
            
            pred_dict[file]["error"][event] = abs(len(event_info_list) - len(pred_dict[file]['event'][event]))
            total_error += pred_dict[file]["error"][event]
            confusion_matrix[len(event_info_list), min(len(pred_dict[file]['event'][event]), 9)] += 1
        
    print("#### Frequency absolute error times/event:", round(total_error / total_test_num, 3), '\n', "confusion_matrix:\n", confusion_matrix)
    return pred_dict

def calculate_ordering_error(grounding_result):
    refs_dict, pred_dict = grounding_result['refs_dict'], grounding_result['pred_dict']
    total_error, total_test_num = 0, 0
    error_dict = {"non_detect": 0, "occur_error": 0, "overlap_error": 0}
     
    for file, item in tqdm(refs_dict.items()): 
        error_type = ""
        pred_dict[file]["refs_event"] = item['event']
        assert len(item['event']) == 2, "The ordering evaluation ensures the presence of two distinct sound events."
        total_test_num += 1
        event_ordering = list(sorted(item['event'].items(), key=lambda x: x[1][0], reverse=False))
        
        # 0 former, 1 later
        event_former, event_later = event_ordering[0][0], event_ordering[1][0]
        pred_info = pred_dict[file]['whole_event']
        
        if not (set([event_former, event_later]) <= pred_info.keys()): # No events were detected by grounding model
            error_type = "non_detect"
        elif not (pred_info[event_former][0] < pred_info[event_later][0]): # Occurrence sequence error
            error_type = "occur_error"
        else:
            min_duration = min([info[2] for info in pred_info.values()])
            if not ((pred_info[event_former][1] - pred_info[event_later][0]) < 0.5 *  min_duration): # Overlap too long
                error_type = "overlap_error"

        if error_type != "":
            pred_dict[file]["error"] = error_type
            error_dict[error_type] += 1

    total_error = sum(error_dict.values())

    print("#### Ordering error rate:", round(total_error / total_test_num, 3))
    return pred_dict

def parse_args():
    parser = argparse.ArgumentParser(description="Inference for text to audio generation task.")
    parser.add_argument(
        "--grounding_ckpt_path", "-g", type=str, default="steam/grounding_tool/grounding_ckpt",
        help="The path to the audio-text grounding model checkpoint",
    )
    parser.add_argument(
        "--generated_path", "-p", type=str, required=True,
        help="The path to the generated audio.",
    )
    parser.add_argument(
        "--reference_path", "-r", type=str, default="data/AudioCap-Strong/test",
        help="The path to the reference json_file.",
    )
    parser.add_argument(
        "--task_name", "-t", type=str, default="ordering",
        choices=["timestamp", "duration", "frequency", "ordering"],
    )
    args = parser.parse_args()

    return args

def main():
    args = parse_args()

    args.generated_path = Path(args.generated_path)
    args.test_json_path = Path(args.reference_path) / f"{args.task_name}_caption.json"
    grounding_result = get_grounding_result(args)
    if args.task_name == "timestamp":
        output = calculate_sed_metric(ref_list=grounding_result['refs_list'], pred_list=grounding_result['pred_list'])
    elif args.task_name == "duration":
        output = calculate_duration_error(grounding_result)
    elif args.task_name == "frequency":
        output = calculate_frequency_error(grounding_result)
    else:
        assert args.task_name == "ordering"
        output = calculate_ordering_error(grounding_result)

            


if __name__ == "__main__":
    main()