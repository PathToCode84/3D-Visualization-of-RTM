# 3D-Visualization-of-RTM
Is the main purpose of this repository. Look at www.sofiajust.com to look at the 3D plot of RTM. It's interactive :)

But it includes other code that I use in my bachelor thesis as well.
* The first other code file is an illustration of RTM on a group level in R
* The other R file analyses bmi z-scores of elementary school children using the National Longitudial Survey 1979 (NLSY79) data

## Render static site

Use these settings if you create the site manually in Render:

- Service type: Static Site
- Build command: `pip install -r requirements.txt && python visualization-stigler1997.py`
- Publish directory: `public`

The build command generates `public/index.html` from the Plotly figure.
