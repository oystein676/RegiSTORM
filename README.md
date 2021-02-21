# RegiSTORM
RegiSTROM project


Using the software: 
1. Run RegiSTROM.exe
2. Start defining jobs by clicking '+'.
3. In the job defintion add the task name, the files of interest (by clicking 'browse' and selecting the files) and select the file that is going to be used as the reference for the transformation.
5. Define the Fiduicial size (diameter), variance limit, and the mean tolerance. 
6. Define the output folder for the corrected files and the suffix that will be added to the corrected file.
7. Click add to add the defined job.
8. Repeat for all jobs required. 
9. Once all jobs are defined, click run to start the registration process.

Advanced settings - When defining a job, it is also possible to change the advanced settings.  
Under advanced settings there is the possibility to change:
- Between fiducial mode (tries to identify fiducials) and cluster mode (tries to identify clusters of localizations). 
- The registration tolerance, sigma, which is the number of standard deviations away from the mean distance a distance between two nearest neighbors can be before they're considered an outlier. 
- Whether or not the identified fiducial should be deleted after the corrections (Everything within the defined radius of the identified fiduial will be removed).
- Which frame range [start, stop] the alorithm will use when identifying the fiducials/cluster.

Variables: 
- Fidusial Size - The diameter of the fiducial / the diameter of the cluster
- Variance Limit (Only applicable for fiducial mode) - The maximum variance in number of localizations per frame within the tolerance (2x the radius of the fiducial) before it is rejected as a fiduical.
- Mean tolerance (Only applicable for fiducial mode) - The minium average of localizations  per frame within the tolerance (2x the radius of the fiducial) before it is rejected as a fiduical.
- Fiducial mode/ Cluster mode - Whether the algorithm should try to identify fiducials (using the variance limit and mean tolerance) or look for cluster of localizations. 
- Registration Tolerance - In the ICP algorithm, pairs of identified fudicials are matched through a nearest neighbor algorithm. The registration tolerance is the number of standard deviations (sigmas) greater than the mean distance the distance between a pair could be before the pair is considered an outlier. 
- Whether the fiducials should be deleted (Only applicable for fiducial mode) - Whether or not the algorithm should delete any localizations that are within the radius of the fiducial from the coordinate of an identified fiducial. 
- The number of frame (per channel) - For which frame range [start, stop] the algorithm should use for a channel when trying to identify the fiducials or clusters.
