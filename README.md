# AudioCap-Strong
[![arXiv](https://img.shields.io/badge/arXiv-2308.05734-brightgreen.svg?style=flat-square)]() 
[![githubio](https://img.shields.io/badge/GitHub.io-Audio_Samples-blue?logo=Github&style=flat-square)](https://zeyuxie29.github.io/AudioCap-Strong/)

 we present a strongly aligned audio-text dataset, AudioCap-Strong. 
 It provides text annotations rich in temporal information such as timestamps, duration, frequency, interval, and ordering, covering almost all aspects of temporal control. 
 Additionally, we offer a comprehensive test set and evaluation metrics STEAM to assess the temporal control performance of various models. 

 ## Dataset
Download the audio files from [AudioCap-Strong(all)](https://drive.google.com/file/d/1-uW9Gler_sfynIxFSaES2pYhMPR3yX3n/view?usp=sharing) or [AudioCap-Strong(test)](https://drive.google.com/file/d/1Xdpc7oY2oK4edUJCUW-vknQaNTBOpE1T/view?usp=sharing).

Audio samples can be found in the [AudioCap-Strong-Demo](https://zeyuxie29.github.io/AudioCap-Strong/). There are four types of alignment signals:
(a).Ordering: "A yip occurs, _followed_ by a bleat after a short pause."
(b).Duration: "A water tap or faucet ran _for 4.33 seconds_."
(c).Frequency: "Sanding occurs _once_, followed by throat clearing _twice_."
(d).Timestamp: "An explosion occurs _from 0.947 to 2.561 seconds_, and then breaking sounds are heard _from 4.368 to 5.790 seconds_."
Caption files are available at [AudioCap-Strong(caption)]. 
These files record the corresponding audio ID, captions, and metadata. 

The metadata for the four tasks is recorded as follows:

(a).Ordering: On- & off-set timestamps.
(b).Duration: Duration of event occurrences.
(c).Frequency: The onset timestamps of events.
(d).Timestamp: On- & off-set timestamps of events.

 ## STEAM

we propose STEAM (Strongly TEmporally-Aligned evaluation Metrics). 
STEAM is a text-based metric that evaluates whether the generated audio segments meet the control requirements specified by the input text. 
An audio-text grounding model is employed to detect the onset and offset of events in generated audio. 
STEAM assesses control performance based on detected timestamps and the control signal provided by the input free text.
The testing script is available at [STEAMtool](https://github.com/zeyuxie29/AudioCap-Strong/tree/main/STEAMtool). We test some currently influential TTA generation models.
