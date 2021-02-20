# RegiSTORM
RegiSTROM project


Using the software: 
1. Run RegiSTROM.exe
2. Start defining jobs by clicking '+'
3. In the job defintion add the task name, the files of interest (and select the file that is going to be used as the reference for the transformation).
4. Define the Fiduicial size (diameter), variance limit, and the mean tolerance. 
5. Define the output folder for the corrected files and the suffix that will be added to the corrected file.
6. Click add to add the defined job.
7. Repeat for all jobs required. 
8. Once all jobs are defined, click run to start the registration process.

Advanced settings - When defining a job, it is also possible to change the advanced settings.  
Under advanced settings there is the possibility to change:
- Between fiducial mode (tries to identify fiducials) and cluster mode (tries to identify clusters of localizations). 
- The registration tolerance, sigma, which is the number of standard deviations away from the mean distance a distance between two nearest neighbors can be before they're considered an outlier. 
- Whether or not the identified fiducial should be deleted after the corrections (Everything within the defined radius of the identified fiduial will be removed).
- Which frame range [start, stop] the alorithm will use when identifying the fiducials/cluster.

