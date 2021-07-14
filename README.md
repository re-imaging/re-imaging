# Re-imaging the empirical: statistical visualisation in art and science
## Project Description
_Re-imaging the empirical_ is a research project investigating the visual cultures of machine learning (ML). We are interested in the dominant role that images play in many contemporary ML projects and endeavours from AlphaGo through to style transfer. We have been inquiring into how images are used by ML models and techniques as part of a broader re-contouring of what it is to both see and know the empirical world. We use ML and dataset methods in this project drawn from scientific scholarship – specifically the pre-print repository [arXiv](https://arxiv.org/) – to detect vectors and differences across scientific images; images that have themselves been generated by ML research in statistics, physics, mathematics, computer vision and more.

## Research Outputs

The project has three threads:
- Tracing the genealogies and interrelations of images generated as a result of ML research - see [_Images of the arXiv: reconfiguring large scientific datasets_](https://culturalanalytics.org/article/21374-images-of-the-arxiv-reconfiguring-large-scientific-image-datasets) published in the Journal of Cultural Analytics.
- Developing a new theoretical framework for thinking changes in seeing, images, and perception in a culture(s) of ML - see [_Platform Seeing: Images and their Invisualities_](https://journals.sagepub.com/doi/10.1177/0263276419847508) published in Theory, Culture & Society
- Building a visual explorer web application that foregrounds new ways of seeing and perceiving shaped by ML computation - see [ImageMesh](https://imagemesh.ai/), a practical outcome of this project and an ongoing research tool for exploring a large sample of images published in arXiv articles. We encourage you to follow the errant paths these images generate as they compose and are plied by new modes and practices of machinic observation.

![ImageMesh Visual Explorer screenshot](https://github.com/re-imaging/re-imaging/blob/master/figures/ImageMesh/ImageMesh_Screenshot_NN_2021-07-14.png)
[ImageMesh Visual Explorer](https://imagemesh.ai/)

## Project Outline
### This repository

This GitHub repository contains the code used for the various parts of this project. This includes downloading and extracting the bulk source data from arXiv, cleaning and organising metadata, converting images, visualising slices of the dataset, running classification algorithms, encoding nearest neighbours maps, and generating images using GANs. As such, it is quite a varied and large repository, but it is hoped that some of the scripts and notebooks will be useful for projects accessing arXiv or using ML techniques on large image datasets.

### Steps for downloading, extracting, and converting arXiv images dataset: 
- Downloading and extracting the arXiv source dataset - see [arxiv_extract.sh](https://github.com/re-imaging/re-imaging/blob/master/arxiv-src-scripts/arxiv_extract.sh)
- Creating an SQLite database to index each image and link to metadata - [sqlite-scripts](https://github.com/re-imaging/re-imaging/blob/master/sqlite-scripts)
- Querying dataset for various statistics regarding image formats, dimensions, category distributions etc. - see [statistics](https://github.com/re-imaging/re-imaging/blob/master/statistics), e.g. [general data statistics](https://github.com/re-imaging/re-imaging/blob/master/statistics/data-statistics.org)
- Preparing data by converting all images to uniform sizes using ImageMagick `convert` - see the [image-conversion](https://github.com/re-imaging/re-imaging/tree/master/image-conversion) folder and in particular [convert_images_from_textfile_threaded.py](https://github.com/re-imaging/re-imaging/blob/master/image-conversion/convert_images_from_textfile_threaded.py)

### Additional processes:
- Running machine learning techniques such as image classification and dimensionality reduction across data
- Producing t-SNE maps of the distribution of different image features within subsets of the data
- Generating images using the image dataset using generative adversarial networks

## Image Samples
![Montage of 144 images sampled randomly from the entire arXiv image dataset, images
have been resized to fit within a 240x240 pixel square. Here we see a diverse collection of images.](https://github.com/re-imaging/re-imaging/blob/master/figures/montage/random_montage_144.jpg)

Montage of 144 images sampled randomly from the entire arXiv image dataset, images have been resized to fit within a 240x240 pixel square. Here we see a diverse collection of images. [Image credits.](https://github.com/re-imaging/re-imaging/blob/master/methods/credits.org#montage-12x12-random)

---

![Stackplot of image file extensions for all arXiv preprint submissions by year.](https://github.com/re-imaging/re-imaging/blob/master/figures/image-formats/extensions_stackplot_smaller_v4_legend_text.png)

Stackplot of image file extensions for all arXiv preprint submissions by year.

---

![Relative number of articles per arXiv primary category. Only categories with article counts > 1000 shown.](https://github.com/re-imaging/re-imaging/blob/master/figures/arxiv-cat-relativesize_2xsize.png)

Relative number of articles per arXiv primary category. Only categories with article counts > 1000 shown.

---

![Percentage of articles published in a given category appearing in each year 1991-2018.](https://github.com/re-imaging/re-imaging/blob/master/figures/arxiv-primcat-percent-volume-per-year_2xsize.png)

Percentage of articles published in a given category appearing in each year 1991-2018.

---

![Number of images published per year in each category. Ordered by total images in a category, largest to smallest, top-left to bottom right. Top 16 categories only shown here.](https://github.com/re-imaging/re-imaging/blob/master/figures/average-images-per-paper/plot_images_cat_year_indax_shareY_top16_v2.png)

Number of images published per year in each category. Ordered by total images in a category, largest to smallest, top-left to bottom right. Top 16 categories only shown here.

---

![Average number of images per article by all arXiv categories and years of submission to 2018. Y axis has been scaled to ignore outliers. Arranged in alphabetical order, refer to arXiv for a list of categories http://arxitics.com/help/categories.](https://github.com/re-imaging/re-imaging/blob/master/figures/average-images-per-paper/plot_average_images_articles_cat_year_yaxis-max32_01.png)

Average number of images per article by all arXiv categories and years of submission to 2018. Y axis has been scaled to ignore outliers. Arranged in alphabetical order, refer to arXiv for a list of categories http://arxitics.com/help/categories.

---

![Ratio of diagram/sensor/mixed image classifications predicted using custom ternary classifier. Maximum of 2000 images sampled from any given category-year combination. Categories shown are hand selected.](https://github.com/re-imaging/re-imaging/blob/master/figures/ternary-classifier/plot_ternary_classifier_predictions_subset_mixed_crop.png)

Ratio of diagram/sensor/mixed image classifications predicted using custom ternary classifier. Maximum of 2000 images sampled from any given category-year combination. Categories shown are hand selected.

---

![t-SNE map of 1000 images from arXiv, organised by features extracted from VGG classifier](https://github.com/re-imaging/re-imaging/blob/master/figures/t-SNE/example-tSNE-grid-arxiv1001_1000.jpg)

t-SNE map of 1000 images from arXiv, organised by features extracted from VGG classifier

---

![t-SNE map of images with the primary category of cs.CV (computer science, computer vision) from 2012 from arXiv, organised by features extracted from VGG classifier](https://github.com/re-imaging/re-imaging/blob/master/figures/t-SNE/tSNE_cuda_cs.CV_2012_n2000_p50_2019-06-18_16-35-11.png)

t-SNE map of images with the primary category of cs.CV (computer science, computer vision) from 2012 from arXiv, organised by features extracted from VGG classifier

---

## Code
This repository contains code, statistics, and images produced throughout the project. These materials are mostly concerned with looking at the dataset of all the images, text, and metadata contained within the [arXiv](https://arxiv.org) source files.

For detailed instructions on running the code, please look in the [methods folder](https://github.com/re-imaging/re-imaging/blob/master/methods/):
- detailed instructions on downloading and extracting the arXiv bulk data and OAI metadata in [dataset-methods](https://github.com/re-imaging/re-imaging/blob/master/methods/dataset-method.org)
- step-by-step methods for organising metadata into an SQLite database in [sqlite-method](https://github.com/re-imaging/re-imaging/blob/master/methods/sqlite-method.org)
- process of converting varied image formats to consistent size jpg images in [image-conversion](https://github.com/re-imaging/re-imaging/blob/master/methods/image-conversion.org) (additional examples in the [image-conversion](https://github.com/re-imaging/re-imaging/tree/master/image-conversion) folder)
- basic information about our [computer setup](https://github.com/re-imaging/re-imaging/blob/master/methods/setup.org)
- examples and explanation of project documentation

Code is written using bash, Python, SQLite, jupyter notebooks, and anaconda. Tested on Ubuntu 18.04 with an Intel CPU and NVidia graphics card.

## People
- [Professor Anna Munster](https://research.unsw.edu.au/people/professor-anna-marie-munster), UNSW Art & Design
- [Professor Adrian Mackenzie](https://researchers.anu.edu.au/researchers/mackenzie-a), Australian National University
- [Kynan Tan](https://kynantan.com/), Postdoctoral Fellow, UNSW Art & Design
## Credits
Code uses examples from
- Machine Learning for Artists [ML4A](https://ml4a.github.io)
- Mario Klingemann's [RasterFairy](https://github.com/Quasimondo/RasterFairy)
## Acknowledgements
This project has been supported by an Australian Research Council Discovery Grant.
Thank you to arXiv for use of its open access interoperability.
