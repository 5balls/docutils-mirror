# Author: Florian Pesth
# Copyright: This module has been placed in the public domain.

"""
Directive for the creation of forms (Intended to be used for html forms
but may be useful later for PDF documents or other stuff as well).
"""

__docformat__ = 'reStructuredText'

from docutils import nodes, utils
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives, states
from docutils.nodes import fully_normalize_name, whitespace_normalize_name
from docutils.parsers.rst.roles import set_classes
from docutils.nodes import Element

class form(Element):
    basic_attributes = None
    local_attributes = None
    pass

# phpmode can be:
# 'off' no php is inserted in the output (default)
# 'checkandembedvalue' Values received via get/post are tested for existance and put in place else the default value is put in place
# 'embedvalue' Values received via get/post are put in place without testing (This assumes previous check of $POST_, $GET_, ... variable and does ignores the default values)

class Form(Directive):
    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {'class': directives.class_option,
                   'name': directives.unchanged,
                   'action': directives.unchanged,
                   'target': directives.unchanged,
                   'method': directives.unchanged,
                   'accept-charset': directives.unchanged,
                   'enctype': directives.unchanged,
                   'phpmode': directives.unchanged,
                   'phpvar': directives.unchanged}
    def run(self):
        if not self.content:
            warning = self.state_machine.reporter.warning(
                'Content block expected for the "%s" directive; none found.' % self.name, nodes.literal_block(self.block_text, self.block_text), line=self.lineno)
            return [warning]
        node = form()
        for option in self.option_spec:
            if option in self.options:
                node[option] = self.options[option]
        if 'phpmode' not in node:
            node['phpmode'] = 'off'
        self.state.nested_parse(self.content, self.content_offset, node)
	return [node]

