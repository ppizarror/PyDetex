"""
PyDetex
https://github.com/ppizarror/PyDetex

TEST PIPELINES
Test the pipelines.
"""

from test._base import BaseTest
import pydetex.pipelines as pip


class ParserTest(BaseTest):

    def test_simple(self) -> None:
        """
        Test simple pipeline.
        """
        s = 'Table \\ref{tab:review-rulebased} details the reviewed rule-based methods within floor plan recognition, considering the datasets used (Table \\ref{tab:databases}) and the four categories of tasks, such as (1) \\textit{Graphics separation}, (2) \\textit{Pattern recognition}, (3) \\textit{Vectorization}, and (4) \\textit{Structural modeling}.'
        self.assertEqual(pip.simple(s),
                         'Table 1 details the reviewed rule-based methods within floor plan recognition, considering the datasets used (Table 2) and the four categories of tasks, such as (1) Graphics separation, (2) Pattern recognition, (3) Vectorization, and (4) Structural modeling.')

        # New lines
        s = 'New space \\ and line \\\\Epic'
        self.assertEqual(pip.simple(s), 'New space and line\nEpic')

        # With comments
        s = """
        % Aqui tirar metodos genericos que sean de poco impacto
        % element recogniztion based on their line representation has been widely studied concerning rule-based approachesSeveral other studies have also considered a line representation and retrieval to recognize several structural elements from floor plans.
        Park and Kwon \cite{Park2003} recognized the main walls of apartments using the auxiliary dimension line, where windows can be retrieved as a subproduct. Feltes et al.'s \cite{Feltes2014} work is capable of finding the object's corners in wall-line drawing images by filtering out unnecessary points without changing the overall structure, especially those that appeared through over-segmentation on diagonal lines; also, a wall-gap filling is possible while performing a heuristic criterion. Tang et al. \cite{Tang2017} automatically generated vector drawings by applying various filters, such as gradient, length, gap-filling, line-merging, and connectivity under several millimeter sizes, assuming walls are represented by parallel lines in both vertical and horizontal axis. Pan et al. \cite{GuanghuiPan2017} detected walls and windows considering empirical rules regarding their pixel layouts, where the user must adjust its thresholds. The bearing wall corresponded to black areas, non-bearing walls to parallel, unfilled rectangles, and windows are composed of three to four closer parallel lines. De \cite{De2019} also assumed that only walls are illustrated as thick black lines in a floor plan layout. Thus, thick and thin lines can be distinguished using a morphological transformation; thick lines can be considered walls, whereas arc lines represent doors. On the other hand, in an effort to overcome the lack of a standard notation, de las Heras et al. \cite{DelasHeras2013a} presented an unsupervised wall segmentation using the assumption of them being a repetitive element, rectangular, placed in orthogonal directions, filled with the same pattern and naturally distributed across the plan. Although assumptions might work over a set, they do not consider semantical relationships or work for multiple plan styles. \\\\
        """
        self.assertEqual(pip.simple(s),
                         "Park and Kwon [1] recognized the main walls of apartments using the auxiliary dimension line, where windows can be retrieved as a subproduct. Feltes et al.'s [2] work is capable of finding the object's corners in wall-line drawing images by filtering out unnecessary points without changing the overall structure, especially those that appeared through over-segmentation on diagonal lines; also, a wall-gap filling is possible while performing a heuristic criterion. Tang et al. [3] automatically generated vector drawings by applying various filters, such as gradient, length, gap-filling, line-merging, and connectivity under several millimeter sizes, assuming walls are represented by parallel lines in both vertical and horizontal axis. Pan et al. [4] detected walls and windows considering empirical rules regarding their pixel layouts, where the user must adjust its thresholds. The bearing wall corresponded to black areas, non-bearing walls to parallel, unfilled rectangles, and windows are composed of three to four closer parallel lines. De [5] also assumed that only walls are illustrated as thick black lines in a floor plan layout. Thus, thick and thin lines can be distinguished using a morphological transformation; thick lines can be considered walls, whereas arc lines represent doors. On the other hand, in an effort to overcome the lack of a standard notation, de las Heras et al. [6] presented an unsupervised wall segmentation using the assumption of them being a repetitive element, rectangular, placed in orthogonal directions, filled with the same pattern and naturally distributed across the plan. Although assumptions might work over a set, they do not consider semantical relationships or work for multiple plan styles.")

        # Empty
        self.assertEqual(pip.simple(''), '')

        # Lists
        # noinspection HttpUrlsUsage
        s = """
        \\begin{itemize}
        \item The academic databases 
        Web of Science, % http://uchile.idm.oclc.org/login?url=http://webofknowledge.com/
        Scopus, % http://uchile.idm.oclc.org/login?url=http://www.scopus.com/
        IEEE/IET Xplore, % http://uchile.idm.oclc.org/login?url=http://ieeexplore.ieee.org/
        Science Direct, % http://uchile.idm.oclc.org/login?url=http://www.sciencedirect.com/
        ACM Digital Library, % http://uchile.idm.oclc.org/login?url=https://dl.acm.org/dl.cfm
        ASCE Library, % http://uchile.idm.oclc.org/login?url=http://ascelibrary.org
        ProQuest, % https://uchile.idm.oclc.org/login?url=http://search.proquest.com/computing?accountid=14621
        and Springer % http://uchile.idm.oclc.org/login?url=https://link.springer.com
        were used for article search and selection. Also, online tools Semantic Scholar and Connected Papers were employed to retrieve similar articles powered by AI and visual graphs.
        
        \item Keywords such as \doublequotes{floor plan analysis}, \doublequotes{floor plan recognition and interpretation}, \doublequotes{floor plan segmentation}, \doublequotes{floor plan image}, \doublequotes{apartment structure}, \doublequotes{wall segmentation}, \doublequotes{architectural plan vectorization}, \doublequotes{room and wall retrieval}, \doublequotes{apartment graph}, \doublequotes{object detection in floor plans}, and \doublequotes{parsing floor plan images} were used to search the databases. The search date period ranged from 1995 to \\fecha. For each article, its cross-references and similar works were also considered for revision.
        \\end{itemize}
        """
        self.assertEqual(pip.simple(s),
                         '- The academic databases\nWeb of Science, Scopus, IEEE/IET Xplore, Science Direct, ACM Digital Library, ASCE Library, ProQuest, and Springer were used for article search and selection. Also, online tools Semantic Scholar and Connected Papers were employed to retrieve similar articles powered by AI and visual graphs.\n- Keywords such as "floor plan analysis", "floor plan recognition and interpretation", "floor plan segmentation", "floor plan image", "apartment structure", "wall segmentation", "architectural plan vectorization", "room and wall retrieval", "apartment graph", "object detection in floor plans", and "parsing floor plan images" were used to search the databases. The search date period ranged from 1995 to \\fecha. For each article, its cross-references and similar works were also considered for revision.')

        # Test replacers
        s = 'This is a \\Thetamagic but also \\Theta is not or \\Theta\\Epic or \\Theta\n sad'
        t = 'This is a \\Thetamagic but also Θ is not or Θ\Epic or Θ\nsad'
        self.assertEqual(pip.simple(s), t)

    def test_strict(self) -> None:
        """
        Strict pipeline.
        """
        s = 'This contains \\insertimageanother{\label{1}}{2}{3}commands, but must be removed!\\'
        self.assertEqual(pip.strict(s), 'This contains commands, but must be removed!')
        s = 'This \\quoteepic{code removed!}is removed\\totally. Not epic \\cite{nice}'
        self.assertEqual(pip.strict(s), 'This is removed. Not epic [1]')
        s = 'This \\quoteepic{code removed!}is removed \\totally nice. Not epic \\cite{nice}'
        self.assertEqual(pip.strict(s), 'This is removed nice. Not epic [1]')

        s = """Write or paste here your \\texttt{LaTeX} code. It simply removes all tex-things and returns a friendly plain text!
        The following is a excellent figure:
        
        \\begin{figure}
          \centering
            \\reflectbox{%
              \includegraphics[width=0.5\\textwidth]{gull}}
          \caption{A picture of the same gull
                   looking the other way!}
        \end{figure}
        
        well $nothing has happened really$ epic $\\alpha$
        """
        t = """Write or paste here your LaTeX code. It simply removes all tex-things and returns a friendly plain text!
The following is a excellent figure:

CAPTION: A picture of the same gull looking the other way!

well EQUATION_0 epic α"""
        self.assertEqual(pip.strict(s), t)

        s = """Yamasaki et al. \cite{Yamasaki2018} also presented a fully convolutional end-to-end FCN network to label pixels in apartment floor plans by performing a general semantic segmentation, ignoring spatial relations between elements and room boundary. The classified pixels from 12 classes formed a graph to model the structure and measure the structural similarity for apartment retrieval. % \\\\% 1
        
        \insertimage[\label{unetmodel}]{unet_compressed}{width=\linewidth}{A U-Net model which segments the walls from a rasterized floor plan image. Layer legend: \\textit{(yellow)} convolutional block, \\textit{(orange)} max-pool, \\textit{(blue)} up-sampling, and \\textit{(purple)} softmax.}% The encoder, comprised of several de-convolutions, captures the context and finer grain structures. Conversely, the decoder reconstruct the output segmented image, combining spatial information from the encoder.}
        
        % U-NET
        A U-Net approach was introduced by Yang \eta \etal \cite{Yang2018}, alongside the pixel deconvolutional layers PixelDCL \cite{Gao2017} to avoid checkerboard artifacts while segmenting walls and doors. """
        t = """Yamasaki et al. [1] also presented a fully convolutional end-to-end FCN network to label pixels in apartment floor plans by performing a general semantic segmentation, ignoring spatial relations between elements and room boundary. The classified pixels from 12 classes formed a graph to model the structure and measure the structural similarity for apartment retrieval.

FIGURE_CAPTION: A U-Net model which segments the walls from a rasterized floor plan image. Layer legend: (yellow) convolutional block, (orange) max-pool, (blue) up-sampling, and (purple) softmax.

A U-Net approach was introduced by Yang η [2], alongside the pixel deconvolutional layers PixelDCL [3] to avoid checkerboard artifacts while segmenting walls and doors."""
        self.assertEqual(pip.strict(s), t)

        s = """Discriminator architectures \cite{Dong2021}.


\insertimage[\label{pix2pix2model}]{pix2pix_compressed}{width=\linewidth}{Pix2Pix model, which translates the rasterized floor plan image style into a segmented format.}

Concerning the recognition and generation of floor plans, Huang and Zheng \cite{Huang2018} introduced an application of Pix2PixHD \cite{Wang2018} to detect rooms from 8 classes, which were colorized to generate a new image. In this example, the conditional GANs lead to translate the raster plan to a segmented style using annotated pairs, classifying each pixel while also preserving the underlying structure of the image. Pix2Pix was also adopted by Kim et al. \cite{Kim2021, Kim2018} to transform plans into 
        """
        t = """Discriminator architectures [1].

FIGURE_CAPTION: Pix2Pix model, which translates the rasterized floor plan image style into a segmented format.

Concerning the recognition and generation of floor plans, Huang and Zheng [2] introduced an application of Pix2PixHD [3] to detect rooms from 8 classes, which were colorized to generate a new image. In this example, the conditional GANs lead to translate the raster plan to a segmented style using annotated pairs, classifying each pixel while also preserving the underlying structure of the image. Pix2Pix was also adopted by Kim et al. [4, 5] to transform plans into"""
        self.assertEqual(pip.strict(s), t)
