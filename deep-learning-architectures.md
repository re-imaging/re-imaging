<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#sec-1">1. Deep Learning Architecture Comparison</a>
<ul>
<li><a href="#sec-1-1">1.1. Motivation and Aims</a></li>
<li><a href="#sec-1-2">1.2. Dataset</a></li>
<li><a href="#sec-1-3">1.3. Latest in Generative Models</a></li>
<li><a href="#sec-1-4">1.4. Architectures</a>
<ul>
<li><a href="#sec-1-4-1">1.4.1. General Models</a></li>
<li><a href="#sec-1-4-2">1.4.2. Discrimination and Classification</a></li>
<li><a href="#sec-1-4-3">1.4.3. Memory Networks</a></li>
<li><a href="#sec-1-4-4">1.4.4. Image Generation</a></li>
</ul>
</li>
<li><a href="#sec-1-5">1.5. Implementations</a>
<ul>
<li><a href="#sec-1-5-1">1.5.1. Deep Convolutional Neural Networks (classification)</a></li>
<li><a href="#sec-1-5-2">1.5.2. Generative Adversarial Networks</a></li>
<li><a href="#sec-1-5-3">1.5.3. Variational Auto-Encoders (VAE)</a></li>
</ul>
</li>
<li><a href="#sec-1-6">1.6. Conclusion</a></li>
</ul>
</li>
</ul>
</div>
</div>

# Deep Learning Architecture Comparison<a id="sec-1" name="sec-1"></a>

## Motivation and Aims<a id="sec-1-1" name="sec-1-1"></a>

This brief survey has been undertaken in order to establish a general scope of practices in the field of Deep Learning architectures. It is particularly focused on deep learning,  primarily those that have been successfully used towards image or text generation. Deep Learning is here defined as any machine learning task that utilises multi-layer neural networks.

The goal of the larger project is to generate images (figures) and text using the arXiv database in order to explore the use of machine learning and statistical methods on this data to generate new models. We will also attempt to generate text using text data.

The aim here is to provide a brief overview comparing particular architectures at the highest level, and then discuss some specific implementations. This overview should help provide an overview of current practices in deep learning, especially generative models. It should also reduce the time spent exploring particular architectures in terms of experimentation and training time.

## Dataset<a id="sec-1-2" name="sec-1-2"></a>

The arXiv dataset consists of approximately 1.5 million e-prints in Physics, Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, Statistics, Electrical Engineering and Systems Science, and Economics [ref: <https://arxiv.org/>]. These are downloadable via Amazon S3 as either PDFs or source data. The source data generally consists of LaTex files with accompanying images that are used to generate the PDFs. Some of the texts/authors do not provide their source and are only downloadable as PDF files.

We have also downloaded the associated metadata for the entire database in the form of individual xml files for each e-print. This metadata contains the title, authors, abstract, field and category of research, and date of publication.

Each e-print is formatted within an expected framework for the structuring of academic scientific and mathematical texts. The text components are generally divided into title, authors, abstract, and body text; with the text generally conforming to a structure of introduction, methods, results, and conclusion. Within these e-prints there are a number of images or figures that are typically given a figure number and caption. The figure number, caption, location within the paper (i.e. which section of the structure) and associated metadata of the e-print could be used as labels for the images. Image data could also be used as unlabelled training data, and some models may be able to 'learn' various features of the data in order to interpolate through them.

This document covers both supervised and unsupervised learning options, as we have not yet determined the use and labelling of data. There is also the option of using semi-supervised training or of exploring the latent space of the distribution in an attempt to move between different labels (such as field of research, or other potential labels).

The images found in papers generally relate to science, mathematics, and computing, and therefore often take the form of graphs, equations, or figures, as well as some photographic images such as examples of image classification/generation. It seems that being able to render high detail images (not necessarily high resolution) that are clear and sharp would give the best results for this particular dataset.

Note: Generative Adversarial Networks and other similar models are typically considered to be unsupervised learning algorithms. They do not use labels in their training data. While training, these models label images as either generated or from the dataset (fake or real), which is used with the classifier to more accurately model the data (i.e. density estimation).

## Latest in Generative Models<a id="sec-1-3" name="sec-1-3"></a>

It appears that the state of the art in image generation continues to be found in Generative Adversarial Networks (GANs) and some of the more interesting recent developments are coming from the NVidia research group. GANs primarily operate on unlabelled training data and instead attempt to create images that fit within the probability distribution of the training data.

The latest NVidia projects have been working with large datasets of facial images (celebrity images from the soon-to-be-released FFHQ dataset), as well as CIFAR and LSUN. They use different techniques to generate ways of moving through the 'feature space' and interpolating through latent space and between different images that are still close to the patterns of the dataset. The latest paper (Dec 2018) uses a style transfer approach in conjunction with progressively trained GANs to be able to interpolate smoothly between images. See StyleGAN video <https://www.youtube.com/watch?time_continue=3&v=kSLJriaOumA> and paper <https://arxiv.org/abs/1812.04948> (and related Progressive GANs <https://arxiv.org/abs/1710.10196>). (Interestingly they also do a fair bit of post-processing of their "results" images). 

The other recent image generation models of interest are the BigGAN <https://arxiv.org/abs/1809.11096> from Google and the StackGAN <https://arxiv.org/abs/1710.10916>. There are also a few non-GAN approaches such as Variational Auto-Encoders, Flow-based Deep Generative Models, and De-Convolutional Inverse Graphics Networks but they aren't discussed as much as GANs at the moment and don't seem to get the same results in terms of image quality, but might be worth investigating because they are (at times) quicker and simpler to train and can produce solid results.

There are a huge number of variations of GANs [see <https://github.com/hindupuravinash/the-gan-zoo> for list]. This overview only deals with some of the more prominent recent developments and the most commonly mentioned in particular fields. There are also a number of reviews of the field, for example see <https://ieeexplore.ieee.org/document/8195348>. For strictly generative models, see <https://blog.openai.com/generative-models/>; for neural networks see <http://www.asimovinstitute.org/neural-network-zoo/>; for an overview of the field of deep learning see <https://www.nature.com/articles/nature14539>.

## Architectures<a id="sec-1-4" name="sec-1-4"></a>

### General Models<a id="sec-1-4-1" name="sec-1-4-1"></a>

1.  Feed-forward Neural Network (FFNN or NN) (aka vanilla, or just 'neural network')

2.  Deep Neural Network (DNN)

### Discrimination and Classification<a id="sec-1-4-2" name="sec-1-4-2"></a>

Convolutional neural networks are typically used for image classification problems, as they have had much more success recently in terms of accuracy, particularly in the case of using Deep CNNs with large datasets. Convolutional neural networks use multiple layers of convolutional processes that activate based on features in the data (such as edges or other identifying features). These are then reduced in dimensionality using max pooling and stride convolutional layers. These networks also typically use Rectified Linear Units (ReLU) to speed up training (convergence) and introduce non-linearity. The layers are then combined using fully connected layers and a classification is determined using softmax or other functions to calculate a final probability.

This may be of importance to this research if we perform some kind of classification, or if training semi-supervised GANs. More detail on specific implementations of convolutional neural networks below.

1.  Convolutional Neural Network (CNN)

2.  De-convolutional Network (DN)

### Memory Networks<a id="sec-1-4-3" name="sec-1-4-3"></a>

These architectures use memory cells to duplicate the effect of a neural network across a sequence (of time, pixels, audio samples etc.). They are effective for generating sequences of text or sound, and have been used to generate images through implementations such as PixelRNN. The images they generate are typically not as realistic as GANs. Recurrent networks can also have difficulties with exploding/vanishing weights while training. PixelRNN is relatively efficient to train but inference (generating images) can be slow and resource-intensive.

1.  Recurrent Neural Network (RNN)

    <http://karpathy.github.io/2015/05/21/rnn-effectiveness/>

2.  Long Short-Term Memory (LSTM)

    This is a kind of recurrent neural network that uses a particular type of memory cell. These cells have three different gate mechanisms for input, output, and memory.
    <https://medium.com/datathings/the-magic-of-lstm-neural-networks-6775e8b540cd>

3.  Neural Turing Machine

    A type of neural network that has access to external memory. Can solve some complex problems, somewhat similar to LSTM.
    <https://arxiv.org/pdf/1410.5401.pdf>

### Image Generation<a id="sec-1-4-4" name="sec-1-4-4"></a>

Generative networks are generally unsupervised, although some use classifications or images to condition the generated images. Generative networks generally attempt to estimate the density of the data distribution. Different approaches to image generation attempt to create an encoder that can turn a 'code' or set of 'latent variables' into an image that closely resembles the patterns and features of the training data. GANs are the most successful in creating realistic images but can be difficult to train as they require both the generator and discriminator to be working well together. VAEs and Flow-based models are easier to train but generally do not output images that are as realistic. PixelRNN and PixelCNN work relatively efficiently but are computationally expensive.

1.  Generative Adversarial Network (GAN)

    GANs use two models, a generator and a discriminator, which work together to produce high quality images. The generator attempts to create images that closely resemble the training or 'real' data. The discriminator attempts to determine if the image is generated or from the training set. Both networks need to be trained together and must simultaneously improve in accuracy in order to produce images that more closely resemble the training data. The two models are playing a 'minimax game'.
    
    <https://arxiv.org/abs/1406.2661>
    Recent tutorial: <https://towardsdatascience.com/understanding-generative-adversarial-networks-gans-cd6e4651a29>

2.  Variational Auto Encoder (VAE)

    First part of the network encodes an input to a set of latent features, the second part of the network decodes the latent features to an output that closely resembles the input. The latent features are a bottleneck, i.e. use less data to represent a given input/output. Can therefore be used for compression, but can also be used for image generation etc.
    
    Different variations of auto-encoders are able to capture particular individual characteristics within latent features so they can manipulated or interpolated separately, e.g. lighting, angle, position. Generally produces images that are somewhat blurry or less clear than GANs, but are somewhat more stable and therefore easier to train.
    
    <http://kvfrans.com/variational-autoencoders-explained/>

3.  PixelRNN and PixelCNN - WaveNet

    Useful for sound and image generation. For images, these networks work pixel by pixel: each pixel is calculated based on the pixel(s) previous (using p1 as input for p2, p1+p2 as input for p3, etc.). They may also additionally work using pixels from the row above or in a circular area around the current pixel. This gives a good representation of the data distribution but can be somewhat slow in both training and inference.
    
    <https://arxiv.org/abs/1601.06759>
    <https://towardsdatascience.com/auto-regressive-generative-models-pixelrnn-pixelcnn-32d192911173>
    <https://towardsdatascience.com/summary-of-pixelrnn-by-google-deepmind-7-min-read-938d9871d6d9>

4.  Conditional Generative Adversarial Network (cGAN) - pix2pix

    Uses a condition (or set of conditions) on the generator in order to generate a matching output. Implemented recently as pix2pix for image-to-image translation, see <https://phillipi.github.io/pix2pix/>. pix2pix creates a general purpose model that can be trained to perform well on a wide variety of image to image tasks. Examples of success include translating from a drawing of edges to a colour image, or from segmentation markers to near-photographic images. Uses composite loss of a GAN and a regression term.
    
    <https://tcwang0509.github.io/pix2pixHD/>
    Web demo: <https://affinelayer.com/pixsrv/>

5.  Cascaded Refinement Networks (CRN)

    A supervised convolutional network that uses refinement layers. It is conditioned using an input image of segments (such as blobs for cars/trees in a road scene, or furniture/walls in an interior scene) which it uses to produce a pseudo-photorealistic image. Does not use adversarial networks, trained using a direct regression objective.
    
    <https://arxiv.org/abs/1707.09405>
    <https://github.com/CQFIO/PhotographicImageSynthesis>

6.  Generative Latent Nearest Neighbours (GLANN)

    Another non-GAN approach to image generation. Uses aspects of latent embedding learning methods (e.g. GLO) and nearest-neighbour based implicit maximum likelihood estimation (IMLE). Produces good results and does not suffer from some of the problems with training GANs. Can also perform image translation by interpolating across input noise.
    
    Published Dec 2018. <https://arxiv.org/abs/1812.08985v1>

7.  Semi-parametric Image Synthesis (SIMS)

    Another approach to image synthesis from an input conditioning image. Most effective at translating from a segmentation image to a pseudo-photorealistic image, with some parameters for variation.
    
    <https://arxiv.org/abs/1804.10992>
    <https://www.youtube.com/watch?v=U4Q98lenGLQ>
    <https://www.reddit.com/r/MachineLearning/comments/8g9k0s/r_photographic_image_generation_with/>

8.  Flow-based Deep Generative Models (Flow)

    Architecture that explicitly learns the probability distribution of the data p(x) through invertible functions. This means that it is straightforward to train and maps well to the probabilities of the input data. Also avoids using GAN techniques. Main example appears to be GLOW produced by OpenAI. Images produced are not as clear or crisp as state-of-the-art GANs, and manipulating specific features seems to produce many artifacts, however interpolation of z vectors seems to work well (based on examples in OpenAI blog post).
    
    <https://lilianweng.github.io/lil-log/2018/10/13/flow-based-deep-generative-models.html#glow>
    <https://blog.openai.com/glow/>
    <https://github.com/openai/glow>

## Implementations<a id="sec-1-5" name="sec-1-5"></a>

Some of the above describe both the architecture and the specific implementation. Below some of the more specific implementations of networks are covered.

### Deep Convolutional Neural Networks (classification)<a id="sec-1-5-1" name="sec-1-5-1"></a>

These are variations of Deep Convolutional Neural Networks. They vary in size and complexity. Some introduce new features or re-organise layers and neurons in particular ways. The following have largely been tested on the ImageNet dataset and have made incremental improvements in both top-1 and top-5 accuracy for classification.

AlexNet was the first famous CNN.
VGG used 3x3 convolutional filters and placed max pooling layers after each 2 convolutions, doubling the number of filters after each max pooling. VGG is much deeper than AlexNet.
GoogLeNet uses inception modules that use pooling, convolution, and concatenation at different scales.
ResNet uses residual layers, incorporating memory into CNNs. This allows for additional depth while still training effectively..

Pre-trained models for each of these are available at: <https://keras.io/applications/#vgg19>

1.  AlexNet

2.  VGG16 and VGG19

3.  ResNet50

4.  Inception Architectures

    These implementations use "inception modules" which are parallel convolutional processes that can be learned as weights. These allow the model to learn whether it is better to use a 3x3 or 5x5 convolution, for example. These implementations also use 1x1 convolutions as a means towards feature reduction, by having a lower number of filters than the number of features in the input.
    
    1.  Inception v1-3 (GoogLeNet)
    
    2.  InceptionResNetV2

5.  Xception

6.  MobileNet

7.  MobileNetV2

8.  DenseNet

9.  NASNet

### Generative Adversarial Networks<a id="sec-1-5-2" name="sec-1-5-2"></a>

1.  Style GAN

    Latest development from the NVidia research group (Karras, Laine, Aila). A ProgGAN that additionally learns to separate different aspects of the images without supervision. Trained on the Flickr-Faces-HQ dataset (FFHQ) and used to produce images of faces (also demonstrated on cars, bedrooms, and cats). Effectively treats each face as the combination of a number of styles that can be divided into coarse, middle, and fine, each altering the produced image in different ways. These can be combined in different ways so that the latent space can be interpolated and navigated in ways that demonstrate the way that particular styles are combined.
    
    Builds on ProgGAN but attempts to combine this with techniques of style transfer.
    
    <https://www.youtube.com/watch?time_continue=3&v=kSLJriaOumA>
    <https://arxiv.org/abs/1812.04948>

2.  Progressive GAN (PG GAN or ProgGAN)

    Progressive training of GAN used by NVidia to generate high resolution, pseudo-photorealistic images of celebrity faces. Also demonstrated on LSUN and CIFAR categories. Grows both the generator and discriminator progressively. Starts from a low resolution and then adding new layers the model increasingly fine details as training progresses. This helps to speed up and stabilise training, as well as producing high quality, high resolution images.
    <https://github.com/tkarras/progressive_growing_of_gans> (tensorflow)
    <https://arxiv.org/abs/1710.10196>

3.  BigGAN

    A very large-scale GAN created by Google. Trained at largest scale attempted so far, required between 128-512 TPUs for different image sizes. Uses a number of modifications on typical GANs to produce improvements in regularisation and image quality. Uses class conditions to generate images of a particular type (e.g. dog). Uses huge amounts of computing power.
    Some artists and coders have experimented with moving through the latent space [<https://thegradient.pub/bigganex-a-dive-into-the-latent-space-of-biggan/>].
    
    The code implementation is available online, but only through Google's colab service. This offers a GPU system for free for research purposes. Model cannot be downloaded or trained, but can output images according to different z vectors (changing position in the latent space).
    <https://arxiv.org/pdf/1809.11096.pdf>
    <https://tfhub.dev/s?q=biggan>
    <https://colab.research.google.com/github/tensorflow/hub/blob/master/examples/colab/biggan_generation_with_tf_hub.ipynb>

4.  Self Attention GAN (SAGAN)

    A convolutional GAN that introduces a self-attention mechanism. Helps to model dependencies across image regions. Also applies spectral normalisation to the discriminator network, which helps to stabilise training. Creates good images that are crisp and seemingly have good backgrounds and coexisting features. Can produce images according to categories. Has also been used for text to image synthesis.
    
    <https://arxiv.org/abs/1805.08318>
    Code implementation available: <https://github.com/brain-research/self-attention-gan>
    Tutorial: <https://medium.com/@jonathan_hui/gan-self-attention-generative-adversarial-networks-sagan-923fccde790c>

5.  CycleGAN

    Image-to-image translation where the paired data is not available. Able to translate an image from a source domain X to a target domain Y. Similar to style transfer in some regards, able to translate a photographic image to "Monet" (or the reverse), horse to zebra, winter to summer etc. Also able to work from segmentation images to pseudo-photorealistic images (similar to pix2pix et al).
    
    <https://arxiv.org/abs/1703.10593>
    <https://junyanz.github.io/CycleGAN/>

6.  Stack GAN

    GAN that generates high-quality images from text description conditions. Uses multiple stages of GANs that firstly generate primitive shapes and colours, then generates high-resolution images. Creates fairly good quality images, but is sometimes described as "slow".
    
    <https://arxiv.org/abs/1612.03242>
    <https://www.reddit.com/r/MachineLearning/comments/9p3jdz/r_tdls_stackgan_realistic_image_synthesis_with/>
    <https://arxiv.org/abs/1710.10916>

7.  Info GAN

    A GAN that learns latent variables without labels. Attempts to disentangle representations without supervision, e.g. learn latent variables in MNIST such as stroke thickness. This allows individual features such as lighting, pose, or rotation to be changed separately.
    
    Published Jun 2016: <https://arxiv.org/abs/1606.03657>

8.  Wasserstein GAN

    A modification of GANs that attempts to alleviate some of the issues with training.
    <https://arxiv.org/abs/1701.07875>

9.  Deep Convolutional Generative Adversarial Network (DCGAN)

    Paper by Radford from early 2016. Most GANs now use convolutional layers. Proven to be more effective than vanilla neural networks, particularly for image generation.
    <https://github.com/carpedm20/DCGAN-tensorflow>
    <https://arxiv.org/pdf/1511.06434v2.pdf> (original paper)
    
    Pytorch tutorial: <https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html>

### Variational Auto-Encoders (VAE)<a id="sec-1-5-3" name="sec-1-5-3"></a>

1.  Deep Recurrent Attentive Writer (DRAW)

    Uses a spatial mechanism with a sequential VAE framework that allows it to iteratively construct complex images. Published early/mid 2015.
    <https://arxiv.org/abs/1502.04623>

2.  Attend Infer Repeat (AIR)

    "AIR aims to reconstruct an image, but instead of doing it in a single shot, it focuses on interesting image parts one-by-one. The figure below demonstrates AIR’s inner workings. It takes a look at the image, figures out how many interesting parts there are and where they are in the image. It then reconstructs them by painting one-part-at-a-time onto a blank canvas. AIR takes a look at the image, figures out how many interesting parts there are, and reconstructs it by painting one-part-at-a-time onto a blank canvas." &#x2013; Adam Kosiorek [<http://akosiorek.github.io/ml/2017/09/03/implementing-air.html>]
    
    Seems to be an interesting but complicated and somewhat fragile architecture. Only provides examples using multi-MNIST data.
    
    August 2016
    <https://arxiv.org/abs/1603.08575>
    Tutorial for implementation: <http://akosiorek.github.io/ml/2017/09/03/implementing-air.html>
    Update/improvement: <https://arxiv.org/abs/1806.01794>
    Code: <http://pyro.ai/examples/air.html>

3.  DCIGN (Deep Convolutional Inverse Graphics Network)

    This network is a VAE but with CNNs and DNs as encoder and decoder.
    <https://arxiv.org/pdf/1503.03167v4.pdf>

## Conclusion<a id="sec-1-6" name="sec-1-6"></a>

The current state of the art for generating images appears to utilise GANs with various modifications, however there are some other architectures that also do well at image generation. For our dataset size (several million images, potentially divided into different classifications according to research area) perhaps the best approach would be to use a GAN with supervised training, incorporating features from the Progressive GAN and Self Attention GAN in order to improve training stability as well as image quality. The potential problems of using GANs include difficulties in training and instability, as well as requiring large amounts of computing power. Perhaps the best strategy then is to use pre-trained models that can then be trained on our dataset to see if this produces results quickly, as well as testing some existing code implementations of these architectures using a subset of our data. This should provide some indication of which architectures are feasible and likely to produce good results for this particular task.

Many of these models will be able to generate relatively high quality images based on our dataset, as well as be able to learn features of the dataset that could be manipulated and navigated by interpolating between vectors in latent space.

The best performing architecture for text generation appears to still be recurrent neural networks and in particular those using Long Short Term Memory (LSTM). Given the size of our dataset, it is feasible to divide into research area (e.g. mathematics) and then train using this corpus. May produce some interesting results.