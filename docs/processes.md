# Processes
- [BCCAQ](#bccaq)
- [CA](#ca)
- [CI](#ci)
- [QDM](#qdm)
- [Rerank](#rerank)

## BCCAQ
Bias Correction/Constructed Analogues with Quantile mapping reordering. Full statistical downscaling of coarse scale global climate model (GCM) output to a fine spatial resolution.

[Notebook Demo](formatted_demos/wps_BCCAQ_demo.html)

## CA
Constructed Analogue (CA) downscaling algorithm. Starts by spatially aggregating high-resolution gridded observations up to the scale of a GCM. Then it proceeds to bias correcting the GCM based on those observations. Finally, it conducts the search for temporal analogues. the top 30 closest timesteps in the gridded observations. For each of the 30 closest "analogue" timesteps, CA records the integer number of the timestep (indices) and a weight for each of the analogues.

[Notebook Demo](formatted_demos/wps_CA_demo.html)

## CI
CI performs several steps. For the GCM input it calculates daily climate anomalies from a given calibration period (default 1951-2005). These daily GCM anomalies are interpolated to the high-resolution observational grid. These interpolated daily anomalies constitute the "Climate Imprint". The high resolution gridded observations are then grouped into months and a climatology is calculated for each month. Finally the observed climatology is added to the GCM-based climate imprint.

[Notebook Demo](formatted_demos/wps_CI_demo.html)

## QDM
This function performs the QDM algorithm on a cell-by-cell basis for each cell in the spatial domain of the inputted high-res gridded observations. It uses the gridded observations plus the GCM-based output of CI as input to the algorithm and then performs a quantile perturbation/quantile mapping bias correction.

[Notebook Demo](formatted_demos/wps_QDM_demo.html)

## Rerank
Quantile Reranking is the final, critical step in the BCCAQ pipeline. Its purpose is this: since Climate Analogues (CA) gets its high resolution information by using a linear combination of historical daily time series for the domain as a whole, it ends up reintroducing some bias. This is because the quantile mapping bias correction step was performed only at course resolution (of the GCM). Quantile Reranking fixes this by re-applying a simple quantile mapping bias correction at each grid box. The advantage of doing this as a final step is that the downscaling method retains the primary advantage of BCCA: high spatial consistency (e.g. when a storm or a heat wave hits a specific area, it probably also hits neighboring areas, etc.).

[Notebook Demo](formatted_demos/wps_rerank_demo.html)
