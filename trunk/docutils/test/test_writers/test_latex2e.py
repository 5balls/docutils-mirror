# -*- coding: utf8 -*-
#! /usr/bin/env python

# $Id$
# Author: engelbert gruber <grubert@users.sourceforge.net>
# Copyright: This module has been placed in the public domain.

"""
Tests for latex2e writer.
"""

import string
# compatibility module for Python 2.3
if not hasattr(string, 'Template'):
    import docutils._string_template_compat
    string.Template = docutils._string_template_compat.Template

from __init__ import DocutilsTestSupport

def suite():
    settings = {'use_latex_toc': False}
    s = DocutilsTestSupport.PublishTestSuite('latex', suite_settings=settings)
    s.generateTests(totest)
    settings['use_latex_toc'] = True
    s.generateTests(totest_latex_toc)
    settings['use_latex_toc'] = False
    settings['sectnum_xform'] = False
    s.generateTests(totest_latex_sectnum)
    settings['sectnum_xform'] = True
    settings['use_latex_citations'] = True
    s.generateTests(totest_latex_citations)
    settings['stylesheet_path'] = 'data/spam,data/ham.tex'
    s.generateTests(totest_stylesheet)
    settings['embed_stylesheet'] = True
    settings['warning_stream'] = ''
    s.generateTests(totest_stylesheet_embed)
    return s

head_template = string.Template(
r"""$head_prefix% generated by Docutils <http://docutils.sourceforge.net/>
\usepackage{fixltx2e} % LaTeX patches, \textsubscript
\usepackage{cmap} % fix search and cut-and-paste in Acrobat
$requirements
%%% Custom LaTeX preamble
$latex_preamble
%%% User specified packages and stylesheets
$stylesheet
%%% Fallback definitions for Docutils-specific commands
$fallbacks$pdfsetup
$titledata
%%% Body
\begin{document}
""")

parts = dict(
head_prefix = r"""\documentclass[a4paper]{article}
""",
requirements = r"""\usepackage{ifthen}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
""",
latex_preamble = r"""% PDF Standard Fonts
\usepackage{mathptmx} % Times
\usepackage[scaled=.90]{helvet}
\usepackage{courier}
""",
stylesheet = '',
fallbacks =  '',
pdfsetup = r"""
% hyperlinks:
\ifthenelse{\isundefined{\hypersetup}}{
  \usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
  \urlstyle{same} % normal text font (alternatives: tt, rm, sf)
}{}
""",
titledata = '')

head = head_template.substitute(parts)

head_table = head_template.substitute(
    dict(parts, requirements = parts['requirements'] +
r"""\usepackage{longtable,ltcaption,array}
\setlength{\extrarowheight}{2pt}
\newlength{\DUtablewidth} % internal use in tables
"""))

head_textcomp = head_template.substitute(
    dict(parts, requirements = parts['requirements'] +
r"""\usepackage{textcomp} % text symbol macros
"""))

totest = {}
totest_latex_toc = {}
totest_latex_sectnum = {}
totest_latex_citations = {}
totest_stylesheet = {}
totest_stylesheet_embed = {}

totest['url_chars'] = [
["http://nowhere/url_with%28parens%29",
head + r"""
\url{http://nowhere/url_with\%28parens\%29}

\end{document}
"""],
]

totest['textcomp'] = [
["2 µm is just 2/1000000 m",
head_textcomp + r"""
2 µm is just 2/1000000 m

\end{document}
"""],
]

totest['spanish quote'] = [
[".. role:: language-es\n\nUnd damit :language-es:`basta`!",
head_template.substitute(dict(parts, requirements =
r"""\usepackage{ifthen}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[spanish,english]{babel}
\addto\shorthandsspanish{\spanishdeactivate{."~<>}}
""")) + r"""
Und damit \otherlanguage{spanish}{basta}!

\end{document}
"""],
]

totest['table_of_contents'] = [
# input
["""\
.. contents:: Table of Contents

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.
""",
## # expected output
head_template.substitute(dict(parts, fallbacks = r"""
% title for topics, admonitions and sidebar
\providecommand*{\DUtitle}[2][class-arg]{%
  % call \DUtitle#1{#2} if it exists:
  \ifcsname DUtitle#1\endcsname%
    \csname DUtitle#1\endcsname{#2}%
  \else
    \smallskip\noindent\textbf{#2}\smallskip%
  \fi
}
""")) + r"""
\phantomsection\label{table-of-contents}
\pdfbookmark[1]{Table of Contents}{table-of-contents}
\DUtitle[contents]{Table of Contents}
%
\begin{list}{}{}

\item \hyperref[title-1]{Title 1}
%
\begin{list}{}{}

\item \hyperref[title-2]{Title 2}

\end{list}

\end{list}


%___________________________________________________________________________

\section*{\phantomsection%
  Title 1%
  \addcontentsline{toc}{section}{Title 1}%
  \label{title-1}%
}

Paragraph 1.


%___________________________________________________________________________

\subsection*{\phantomsection%
  Title 2%
  \addcontentsline{toc}{subsection}{Title 2}%
  \label{title-2}%
}

Paragraph 2.

\end{document}
"""],

]

totest_latex_toc['no_sectnum'] = [
# input
["""\
.. contents::

first section
-------------
""",
## # expected output
head + r"""
\phantomsection\label{contents}
\pdfbookmark[1]{Contents}{contents}
\tableofcontents



%___________________________________________________________________________

\section*{\phantomsection%
  first section%
  \addcontentsline{toc}{section}{first section}%
  \label{first-section}%
}

\end{document}
"""],
]

totest_latex_toc['sectnum'] = [
# input
["""\
.. contents::
.. sectnum::

first section
-------------
""",
## # expected output
head + r"""
\phantomsection\label{contents}
\pdfbookmark[1]{Contents}{contents}
\tableofcontents



%___________________________________________________________________________

\section*{\phantomsection%
  1~~~first section%
  \addcontentsline{toc}{section}{1~~~first section}%
  \label{first-section}%
}

\end{document}
"""],
]


totest_latex_sectnum['no_sectnum'] = [
# input
["""\
some text

first section
-------------
""",
## # expected output
head_template.substitute(dict(parts, requirements = parts['requirements'] +
r"""\setcounter{secnumdepth}{0}
""")) + r"""
some text


%___________________________________________________________________________

\section{first section%
  \label{first-section}%
}

\end{document}
"""],
]

totest_latex_sectnum['sectnum'] = [
# input
["""\
.. sectnum::

some text

first section
-------------
""",
## # expected output
head + r"""
some text


%___________________________________________________________________________

\section{first section%
  \label{first-section}%
}

\end{document}
"""],
]

totest_latex_citations['citations_with_underscore'] = [
# input
["""\
Just a test citation [my_cite2006]_.

.. [my_cite2006]
   The underscore is mishandled.
""",
## # expected output
head + r"""
Just a test citation \cite{my_cite2006}.

\begin{thebibliography}{my\_cite2006}
\bibitem[my\_cite2006]{my_cite2006}{
The underscore is mishandled.
}
\end{thebibliography}

\end{document}
"""],
]


totest_latex_citations['adjacent_citations'] = [
# input
["""\
Two non-citations: [MeYou2007]_[YouMe2007]_.

Need to be separated for grouping: [MeYou2007]_ [YouMe2007]_.

Two spaces (or anything else) for no grouping: [MeYou2007]_  [YouMe2007]_.

But a line break should work: [MeYou2007]_
[YouMe2007]_.

.. [MeYou2007] not.
.. [YouMe2007] important.
""",
# expected output
head + r"""
Two non-citations: {[}MeYou2007{]}\_{[}YouMe2007{]}\_.

Need to be separated for grouping: \cite{MeYou2007,YouMe2007}.

Two spaces (or anything else) for no grouping: \cite{MeYou2007}  \cite{YouMe2007}.

But a line break should work: \cite{MeYou2007,YouMe2007}.

\begin{thebibliography}{MeYou2007}
\bibitem[MeYou2007]{MeYou2007}{
not.
}
\bibitem[YouMe2007]{YouMe2007}{
important.
}
\end{thebibliography}

\end{document}
"""],
]


totest['enumerated_lists'] = [
# input
["""\
1. Item 1.
2. Second to the previous item this one will explain

  a) nothing.
  b) or some other.

3. Third is 

  (I) having pre and postfixes
  (II) in roman numerals.
""",
# expected output
head + r"""\newcounter{listcnt0}
\begin{list}{\arabic{listcnt0}.}
{
\usecounter{listcnt0}
\setlength{\rightmargin}{\leftmargin}
}

\item Item 1.

\item Second to the previous item this one will explain
\end{list}
%
\begin{quote}
\setcounter{listcnt0}{0}
\begin{list}{\alph{listcnt0})}
{
\usecounter{listcnt0}
\setlength{\rightmargin}{\leftmargin}
}

\item nothing.

\item or some other.
\end{list}

\end{quote}
\setcounter{listcnt0}{0}
\begin{list}{\arabic{listcnt0}.}
{
\usecounter{listcnt0}
\addtocounter{listcnt0}{2}
\setlength{\rightmargin}{\leftmargin}
}

\item Third is
\end{list}
%
\begin{quote}
\setcounter{listcnt0}{0}
\begin{list}{(\Roman{listcnt0})}
{
\usecounter{listcnt0}
\setlength{\rightmargin}{\leftmargin}
}

\item having pre and postfixes

\item in roman numerals.
\end{list}

\end{quote}

\end{document}
"""],
]

# BUG: need to test for quote replacing if language is de (ngerman).

totest['quote_mangling'] = [
# input
["""
Depending on language quotes are converted for latex.
Expecting "en" here.

Inside literal blocks quotes should be left untouched
(use only two quotes in test code makes life easier for
the python interpreter running the test)::

    ""
    This is left "untouched" also *this*.
    ""

.. parsed-literal::

    should get "quotes" and *italics*.


Inline ``literal "quotes"`` should be kept.
""",
head + r"""
Depending on language quotes are converted for latex.
Expecting ``en'' here.

Inside literal blocks quotes should be left untouched
(use only two quotes in test code makes life easier for
the python interpreter running the test):
%
\begin{quote}{\ttfamily \raggedright \noindent
"{}"\\
This~is~left~"untouched"~also~*this*.\\
"{}"
}
\end{quote}
%
\begin{quote}{\ttfamily \raggedright \noindent
should~get~"quotes"~and~\emph{italics}.
}
\end{quote}

Inline \texttt{literal "quotes"} should be kept.

\end{document}
"""],
]

totest['table_caption'] = [
# input
["""\
.. table:: Foo

   +-----+-----+
   |     |     |
   +-----+-----+
   |     |     |
   +-----+-----+
""",
head_table + r"""
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable}[c]{|p{0.075\DUtablewidth}|p{0.075\DUtablewidth}|}
\caption{Foo}\\
\hline
 &  \\
\hline
 &  \\
\hline
\end{longtable}

\end{document}
"""],
]

totest['table_class'] = [
# input
["""\
.. table::
   :class: borderless

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
   |  3  |  4  |
   +-----+-----+
""",
head_table + r"""
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable*}[c]{p{0.075\DUtablewidth}p{0.075\DUtablewidth}}

1
 & 
2
 \\

3
 & 
4
 \\
\end{longtable*}

\end{document}
"""],
]

# The "[" needs to be protected (otherwise it will be seen as an
# option to "\\", "\item", etc. ).

totest['brackett_protection'] = [
# input
["""\
::

  something before to get a end of line.
  [

  the empty line gets tested too
  ]
""",
head + r"""%
\begin{quote}{\ttfamily \raggedright \noindent
something~before~to~get~a~end~of~line.\\
{[}\\
~\\
the~empty~line~gets~tested~too\\
{]}
}
\end{quote}

\end{document}
"""],
]

totest['raw'] = [
[r""".. raw:: latex

   $E=mc^2$

A paragraph.

.. |sub| raw:: latex

   (some raw text)

Foo |sub|
same paragraph.
""",
head + r"""
$E=mc^2$

A paragraph.

Foo (some raw text)
same paragraph.

\end{document}
"""],
]

totest['title_with_inline_markup'] = [
["""\
This is the *Title*
===================

This is the *Subtitle*
----------------------

This is a *section title*
~~~~~~~~~~~~~~~~~~~~~~~~~

This is the *document*.
""",
head_template.substitute(
    dict(parts, pdfsetup=parts['pdfsetup'] + r"""\hypersetup{
  pdftitle={This is the Title},
}
""", titledata=r"""%%% Title Data
\title{\phantomsection%
  This is the \emph{Title}%
  \label{this-is-the-title}%
  \\ % subtitle%
  \large{This is the \emph{Subtitle}}%
  \label{this-is-the-subtitle}}
\author{}
\date{}
""")) + r"""\maketitle


%___________________________________________________________________________

\section*{\phantomsection%
  This is a \emph{section title}%
  \addcontentsline{toc}{section}{This is a section title}%
  \label{this-is-a-section-title}%
}

This is the \emph{document}.

\end{document}
"""],
]

totest_stylesheet['two-styles'] = [
# input
["""two stylesheet links in the header""",
head_template.substitute(dict(parts, stylesheet =
r"""\usepackage{data/spam}
\input{data/ham.tex}
""")) + r"""
two stylesheet links in the header

\end{document}
"""],
]

totest_stylesheet_embed['two-styles'] = [
# input
["""two stylesheets embedded in the header""",
head_template.substitute(dict(parts, stylesheet =
r"""% Cannot embed stylesheet 'data/spam.sty':
%   No such file or directory.
% embedded stylesheet: data/ham.tex
\newcommand{\ham}{wonderful ham}

""")) + r"""
two stylesheets embedded in the header

\end{document}
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
