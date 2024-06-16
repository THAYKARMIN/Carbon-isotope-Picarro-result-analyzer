# Carbon isotope Picarro result analyzer

## Background

Carbon fixation in plants is the process of taking carbon dioxide (CO2) from the air and turning it into sugars that the plant can use for energy and growth. This happens during photosynthesis in the plant's leaves, and it also releases oxygen (O2) into the air. In most plants (C3 plants), CO2 is directly used in a cycle of reactions to produce these sugars. In some plants (C4 and CAM plants), there are extra steps that help them capture CO2 more efficiently, especially in hot and dry conditions


The CO2 in the atmosphere is composed of different carbon isotopes, and specifically the ratio of stable isotopes 13C and 12C, expressed as δ13C:

provides valuable insights into plant physiology and particularly drought stress. Under well-watered conditions with open stomata, RuBisCO preferentially fixes the lighter 12C that diffuses a little bit faster and also has a higher affinity for the 12C isotope over 13C. This results in more negative δ13C values (higher 13C discrimination). When stomata close due to drought stress, intercellular CO2 concentrations are lower, and RuBisCO has a reduced ability to discriminate against the heavier 13C isotope during carboxylation, resulting in less negative δ13C values.

The analysis of carbon isotopes is done with a Picarro analyzer built on Cavity Ring-Down Spectroscopy (CRDS) technology. This sophisticated time-based measurement uses a laser to quantify spectral features of gas-phase molecules in an optical cavity and measures the 12C and 13C values of a sample. The Picarro provides a CSV file with the analysis, including the δ13C value, which then needs to be corrected with calibration values and a glucose standard me so:
```
(corrected) δ13C = δ13C - glucose standart mean - calibration value
```
