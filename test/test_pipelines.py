"""
PyDetex
https://github.com/ppizarror/pydetex

TEST PIPELINES
Test the pipelines.
"""

from test._base import BaseTest
import pydetex.pipelines as pip


class ParserTest(BaseTest):

    def test_simple_pipeline(self) -> None:
        """
        Test simple pipeline.
        """
        s = 'Table \\ref{tab:review-rulebased} details the reviewed rule-based methods within floor plan recognition, considering the datasets used (Table \\ref{tab:databases}) and the four categories of tasks, such as (1) \\textit{Graphics separation}, (2) \\textit{Pattern recognition}, (3) \\textit{Vectorization}, and (4) \\textit{Structural modeling}.'
        self.assertEqual(pip.simple_pipeline(s),
                         'Table 1 details the reviewed rule-based methods within floor plan recognition, considering the datasets used (Table 2) and the four categories of tasks, such as (1) Graphics separation, (2) Pattern recognition, (3) Vectorization, and (4) Structural modeling.')

        # New lines
        s = 'New space \\ and line \\\\Epic'
        self.assertEqual(pip.simple_pipeline(s), 'New space and line\nEpic')

        # With comments
        s = """
        % Aqui tirar metodos genericos que sean de poco impacto
        % element recogniztion based on their line representation has been widely studied concerning rule-based approachesSeveral other studies have also considered a line representation and retrieval to recognize several structural elements from floor plans.
        Park and Kwon \cite{Park2003} recognized the main walls of apartments using the auxiliary dimension line, where windows can be retrieved as a subproduct. Feltes et al.'s \cite{Feltes2014} work is capable of finding the object's corners in wall-line drawing images by filtering out unnecessary points without changing the overall structure, especially those that appeared through over-segmentation on diagonal lines; also, a wall-gap filling is possible while performing a heuristic criterion. Tang et al. \cite{Tang2017} automatically generated vector drawings by applying various filters, such as gradient, length, gap-filling, line-merging, and connectivity under several millimeter sizes, assuming walls are represented by parallel lines in both vertical and horizontal axis. Pan et al. \cite{GuanghuiPan2017} detected walls and windows considering empirical rules regarding their pixel layouts, where the user must adjust its thresholds. The bearing wall corresponded to black areas, non-bearing walls to parallel, unfilled rectangles, and windows are composed of three to four closer parallel lines. De \cite{De2019} also assumed that only walls are illustrated as thick black lines in a floor plan layout. Thus, thick and thin lines can be distinguished using a morphological transformation; thick lines can be considered walls, whereas arc lines represent doors. On the other hand, in an effort to overcome the lack of a standard notation, de las Heras et al. \cite{DelasHeras2013a} presented an unsupervised wall segmentation using the assumption of them being a repetitive element, rectangular, placed in orthogonal directions, filled with the same pattern and naturally distributed across the plan. Although assumptions might work over a set, they do not consider semantical relationships or work for multiple plan styles. \\\\
        """
        self.assertEqual(pip.simple_pipeline(s),
                         "Park and Kwon [1] recognized the main walls of apartments using the auxiliary dimension line, where windows can be retrieved as a subproduct. Feltes et al.'s [2] work is capable of finding the object's corners in wall-line drawing images by filtering out unnecessary points without changing the overall structure, especially those that appeared through over-segmentation on diagonal lines; also, a wall-gap filling is possible while performing a heuristic criterion. Tang et al. [3] automatically generated vector drawings by applying various filters, such as gradient, length, gap-filling, line-merging, and connectivity under several millimeter sizes, assuming walls are represented by parallel lines in both vertical and horizontal axis. Pan et al. [4] detected walls and windows considering empirical rules regarding their pixel layouts, where the user must adjust its thresholds. The bearing wall corresponded to black areas, non-bearing walls to parallel, unfilled rectangles, and windows are composed of three to four closer parallel lines. De [5] also assumed that only walls are illustrated as thick black lines in a floor plan layout. Thus, thick and thin lines can be distinguished using a morphological transformation; thick lines can be considered walls, whereas arc lines represent doors. On the other hand, in an effort to overcome the lack of a standard notation, de las Heras et al. [6] presented an unsupervised wall segmentation using the assumption of them being a repetitive element, rectangular, placed in orthogonal directions, filled with the same pattern and naturally distributed across the plan. Although assumptions might work over a set, they do not consider semantical relationships or work for multiple plan styles.")

        # Empty
        self.assertEqual(pip.simple_pipeline(''), '')
