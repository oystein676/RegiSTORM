# RegiSTORM
The RegiSTORM project - To learn more about the project, please read our article (Link TBA).


## Using the software: 
Python needs to be installed on your computer to run the software. 
1. Run RegiSTORM.exe
2. Start defining jobs by clicking '+'.
3. In the job definition add the task name, the files of interest (by clicking 'browse' and selecting the .CSV-files) and select the file that is going to be used as the reference for the transformation.
4. Define the Fiducial size (diameter), variance limit, and the mean tolerance. 
5. Define the output folder for the corrected files and the suffix that will be added to the corrected file.
6. Click ‘add’ to add the defined job.
7. Repeat for all jobs required. 
8. Once all jobs are defined, click ‘run’ to start the registration process
   (the software will freeze between each job being processed).

Advanced settings: When defining a job, it is also possible to change the advanced settings. Under advanced settings there is the possibility to change:
- Between fiducial mode (tries to identify fiducials) and cluster mode (tries to identify clusters of localizations). 
- The registration tolerance, sigma, which is the number of standard deviations away from the mean distance a distance between two nearest neighbors can be before they're considered an outlier. 
- Whether or not the identified fiducial should be deleted after the corrections (Everything within the defined radius of the identified fiducial will be removed).
- Which frame range [start, stop] the algorithm will use when identifying the fiducials/cluster.

Variables: 
- Fiducial Size - The diameter of the fiducial / the diameter of the cluster
- Variance Limit (Only applicable for fiducial mode) - The maximum variance in number of localizations per frame within the tolerance (2x the fiducial radius) before it is rejected as a fiducial.
- Mean tolerance (Only applicable for fiducial mode) - The minimum average of localizations  per frame within the tolerance (2x the fiducial radius) before it is rejected as a fiducial.
- Fiducial mode/Cluster mode - Whether the algorithm should try to identify fiducials (using the variance limit and mean tolerance) or look for clusters of localizations. 
- Registration Tolerance - In the ICP algorithm, pairs of identified fiducials are matched through a nearest neighbor algorithm. The registration tolerance is the number of standard deviations (sigmas) greater than the mean distance the distance between a pair could be before the pair is considered an outlier. 
- Whether the fiducials should be deleted (Only applicable for fiducial mode) - Whether or not the algorithm should delete any localizations that are within the radius of the fiducial from the coordinate of an identified fiducial. 
- The number of frames (per channel) - For which frame range [start, stop] the algorithm should use for a channel when trying to identify the fiducials or clusters.

## Full procedure: 
1. Acquire images using STORM setup.
2. Process data in ThunderSTORM or similar reconstruction software. 
3. Drift correct in ThunderSTORM or likely. Chromatic correction can also increase quality of your data.
4. Export the localizations in .CSV format.
5. Register the files in the RegiSTORM software.
6. Reconstruct the corrected .CSV-files in ThunderSTORM or similar software
7. Do post-processing in ImageJ or other software.

# Cite this work: 
TBA
