# Making a 3D Visualization of the Regression toward the Mean (RTM) effect
.. is the purpose of this repository. You can look at www.rtm.sofiajust.com to see the 3D plot of RTM. It's interactive :)

The graphic was inspired by Stephen M. Stigler's 1997 article *Regression towards the mean, historically considered*.



## Render static site

Use these settings if you create the site manually in Render:

- Service type: Static Site
- Build command: `pip install -r requirements.txt && python visualization-stigler1997.py`
- Publish directory: `public`

The build command generates `public/index.html` from the Plotly figure.
