

# FMG-toolbox

<img src="images/FMG-hex_400.png" width=150 align="right" />
<img src="images/USACE_200.png" width=150 align="right" />

The Forest Management Geodatabase (FMG), FMG-toolbox provides a set of python-based ArcGIS script tools that allow users to accomplish the following:
- Quality control and assure field collected prism, fixed, and age plot surveys
- Calculate a wide range of forest statistics at multiple spatial resolutions
- Generate reports and spatial views of the statistics



## Project Status
[![Maturing](https://img.shields.io/badge/lifecycle-maturing-blue.svg)](https://www.tidyverse.org/lifecycle)
[![Project Status: Active The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![packageversion](https://img.shields.io/badge/Package%20version-v2024.9.1-orange.svg?style=flat-square)](commits/main)
[![Last-changedate](https://img.shields.io/badge/last%20change-2024--09--27-yellowgreen.svg)](commits/main)
[![Licence](https://img.shields.io/badge/licence-CC0-blue.svg)](http://choosealicense.com/licenses/cc0-1.0/)



## Description
<img src="images/ArcGISToolbox.jpg" width=125 align="left"  />

The FMG toolbox is an ESRI ArcGIS toolbox, referencing python scripts configured to run in ArcGIS Pro v3.0 or higher. The tools are used to QA/QC field collected prism, fixed, and age plot surveys, calcualte a wide range of statistics across multiple spatial scales, and generate reports and spatial views of the statistics. The tooling developed is designed to support the specific data collection protocols defined by the [Upper Mississippi River Systemic Forest Stewardship Plan](https://www.mvd.usace.army.mil/Portals/52/docs/regional_flood_risk_management/our_mississippi/UMRSystemicFSP7-26-12.pdf), [Executive Summary](https://www.mvd.usace.army.mil/Portals/52/docs/regional_flood_risk_management/our_mississippi/UMR/UMR%20Systemic%20FSP%20-%20Exec%20Summary%20Aug%202012.pdf) and requires certain data schema definitions to be met. More information can be found in the technical and user manuals.  



## Funding
Funding for development and maintenance of the FMG-toolbox has been provided by the following US Army Corps of Engineers (USACE) programs:

* [St. Paul District, Mississippi River Project](https://www.mvp.usace.army.mil/Missions/Recreation/)
* [Rock Island District, Mississippi River Project](https://www.mvr.usace.army.mil/Missions/Recreation/Mississippi-River-Project/)
* [St. Louis District, Rivers Project Office](https://www.mvs.usace.army.mil/Missions/Recreation/Rivers-Project-Office/)
* [Navigation and Ecosystem Sustainability Program (NESP)](https://www.mvr.usace.army.mil/Rock-Island-District/Programs/NESP/)
* [Upper Mississippi River Restoration Program (UMRR)](https://www.mvr.usace.army.mil/Missions/Environmental-Stewardship/Upper-Mississippi-River-Restoration/)



## Authors
* [Christopher Hawes](mailto:Christopher.C.Hawes@usace.army.mil), Geographer, Rock Island District, U.S. Army Corps of Engineers
* [Alden Ross](mailto:alden.g.ross@usace.army.mil), Geographer, Rock Island District, U.S. Army Corps of Engineers
* [Michael Dougherty](mailto:Michael.P.Dougherty@usace.army.mil), Geographer, Rock Island District, U.S. Army Corps of Engineers <div itemscope itemtype="https://schema.org/Person"><a itemprop="sameAs" content="https://orcid.org/0000-0002-1465-5927" href="https://orcid.org/0000-0002-1465-5927" target="orcid.widget" rel="me noopener noreferrer" style="vertical-align:top;"><img src="https://orcid.org/sites/default/files/images/orcid_16x16.png" style="width:1em;margin-right:.5em;" alt="ORCID iD icon">https://orcid.org/0000-0002-1465-5927</a></div>
* [Andy Meier](Andrew.R.Meier@usace.army.mil), Forester, St. Paul District, U.S. Army Corps of Engineers
* [Ben Vandermyde](mailto:Benjamin.J.Vandermyde@usace.army.mil), Forester, Rock Island District, U.S. Army Corps of Engineers
* [Brian Stoff](Brian.W.Stoff@usace.army.mil), Forester, St. Louis District, U.S. Army Corps of Engineers



## Install and Use
To use the FMG-Toolbox:
- Download the most recent release
- Unzip the download (locally or to a network location)
- In ArcGIS Pro navigate to the location of the unzipped directory then FMG-Toolbox/toolbox which contains the ArcGIS Toolbox file(.atbx)
- Run the relevant script tools from ArcGIS Pro v3.0 or later.



## Latest Updates
Check out the [NEWS](NEWS.md) for details on the latest updates.  



## Bug Reports
If you find any bugs while using the FMG toolbox toolbox, please open an [issue](https://github.com/ForestManagementGeodatabase/FMG-toolbox/issues) in this repository. 



## Developer Note: Configuring PyCharm
These notes are meant for developers actively working on the project or interested in extending the project. They ensure that PyCharm is using the default python environment installed alongside ArcGIS Pro.
1. Set Python Interpreter - Go to File | Setings | Project <Project Name> | Python Interpreter. Configure the source to the ArcGIS Pro python interpreter installed alongside your Pro install. Generally at this path: "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
2. Set Python Terminal - Go to File | Settings | Tools | Terminal. Set the shell path to C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\proenv.bat.
3. Set Python Console - Go to File | Settings | Build, Execution, Deployment | Console. Uncheck the radio button next to 'Use IPython if available'. Note this changes the console to a more IDLE like experience, to continue using the console in a python-notebook like experience, ignore this step.


