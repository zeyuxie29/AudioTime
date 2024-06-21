# AudioCap-Strong
[![arXiv](https://img.shields.io/badge/arXiv-2308.05734-brightgreen.svg?style=flat-square)]() 
[![githubio](https://img.shields.io/badge/GitHub.io-Audio_Samples-blue?logo=Github&style=flat-square)]([https://audioldm.github.io/audioldm2/](https://zeyuxie29.github.io/AudioCap-Strong/))

 we present a strongly aligned audio-text dataset, AudioCap-Strong. 
 It provides text annotations rich in temporal information such as timestamps, duration, frequency, interval, and ordering, covering almost all aspects of temporal control. 
 Additionally, we offer a comprehensive test set and evaluation metrics STEAM to assess the temporal control performance of various models. 

 ## Dataset
Download the dataset from [AudioCap-Strong]().

 ## STEAM

we propose STEAM (Strongly TEmporally-Aligned evaluation Metrics). 
STEAM is a text-based metric that evaluates whether the generated audio segments meet the control requirements specified by the input text. 
An audio-text grounding model is employed to detect the onset and offset of events in generated audio. 
STEAM assesses control performance based on detected timestamps and the control signal provided by the input free text.
The testing script is available at [STEAMtool](https://github.com/zeyuxie29/AudioCap-Strong/tree/main/STEAMtool). We test some currently influential TTA generation models.
