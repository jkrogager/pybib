# -*- coding: UTF-8 -*-

"""
    Implementation of BibTeX handling in python.
    Functions to implement:
     x format_author_list
     x format_journal_name
     - format_full_date
     - format_reference

    A 'bibitem' refers to a dictionary instance containing
    BibTeX bibliographic information, as parsed from 'bibtexparser'.
"""

from pylatexenc import latexencode
from pylatexenc import latex2text

journal_transform = {'aj': u'AJ',
                     'araa': u'ARA&A',
                     'apj': u'ApJ',
                     'apjl': u'ApJ',
                     'apjs': u'ApJS',
                     'apss': u'Ap&SS',
                     'aap': u'A&A',
                     'aapr': u'A&A Rev.',
                     'aaps': u'A&AS',
                     'mnras': u'MNRAS',
                     'memras': u'MmRAS',
                     'nat': u'Nature',
                     'pasp': u'PASP',
                     'aplett': u'Astrophys. Lett.'}


class Author(object):
    def __init__(self, author_string):
        author_string = author_string.strip()
        author_latex = latexencode.utf8tolatex(author_string,
                                               non_ascii_only=True)
        self.latex_names = splitname(author_latex)
        self.unicode_names = splitname(author_string)

        self.last = u' '.join(self.unicode_names['last'])
        self.first = u' '.join(self.unicode_names['first'])
        self.jr = u' '.join(self.unicode_names['jr'])
        self.von = u' '.join(self.unicode_names['von'])

    def print_name(self):
        print format_author_name(self.unicode_names)

    def get_full_name(self):
        return format_author_name(self.unicode_names)

    def get_latex_name(self):
        return format_author_name(self.latex_names)

    def set_last(self, name):
        name_latex = latexencode.utf8tolatex(name)
        self.unicode_names['last'] = name.split(' ')
        self.latex_names['last'] = name_latex.split(' ')
        self.last = name

    def set_first(self, name):
        name_latex = latexencode.utf8tolatex(name)
        self.unicode_names['first'] = name.split(' ')
        self.latex_names['first'] = name_latex.split(' ')
        self.first = name

    def set_jr(self, name):
        name_latex = latexencode.utf8tolatex(name)
        self.unicode_names['jr'] = name.split(' ')
        self.latex_names['jr'] = name_latex.split(' ')
        self.jr = name

    def set_von(self, name):
        name_latex = latexencode.utf8tolatex(name)
        self.unicode_names['von'] = name.split(' ')
        self.latex_names['von'] = name_latex.split(' ')
        self.von = name


def unicode_char_in_string(string):
    try:
        string.encode('ascii')
        return False

    except UnicodeEncodeError:
        return True


def format_editor_list(bib_entry):
    """ Format the list of editors. """
    bibitem = bib_entry.fields
    editor_list = bibitem['editor'].split('and')
    if len(editor_list) > 1:
        editor_id = "(Eds.)"
    else:
        editor_id = "(Ed.)"

    editors = list()
    for editor_field in editor_list:
        editor_field = editor_field.replace('{', '')
        editor_field = editor_field.replace('}', '')
        editor_field = editor_field.replace('~', ' ')
        editors.append(editor_field.strip())
    if len(editors) == 1:
        editor = editors[0]

    elif len(editors) == 1:
        editor = ' and '.join(editors)

    else:
        editor = '; '.join(editors[:-1]) + ' and ' + editors[-1]

    return (editor, editor_id)


def clean_string(string):
    string = string.replace('{', '')
    string = string.replace('}', '')
    string = string.replace('~', ' ')
    return string.strip()


def format_author_list(bib_entry, Nshow=3, Nmax=8, showAll=False):
    """ Convert the BibTeX name list to real text: """

    author_list = bib_entry.fields['author'].split('and')
    authors = list()
    for author_field in author_list:
        # Convert LaTeX to Unicode
        if '\\' in author_field:
            unicode_author = latex2text.latex2text(author_field)
        else:
            unicode_author = author_field
        authors.append(clean_string(unicode_author))

    if showAll:
        if len(authors) == 1:
            field_text = authors[0]

        elif len(authors) == 2:
            field_text = ' and '.join(authors)

        else:
            field_text = '; '.join(authors[:-1]) + ' and ' + authors[-1]

    else:
        if len(authors) == 1:
            field_text = authors[0]

        elif len(authors) == 2:
            field_text = ' and '.join(authors)

        elif len(authors) > Nmax:
            field_text = '; '.join(authors[:Nshow]) + ' et al.'

        elif len(authors) <= Nmax:
            field_text = '; '.join(authors[:-1]) + ' and ' + authors[-1]

        else:
            field_text = '; '.join(authors[:-1]) + ' and ' + authors[-1]

    return field_text


def format_journal_name(bib_entry):
    # Convert the LaTeX shorthand to real text:
    tex_journal = bib_entry.fields['journal'].strip('\\')
    if 'arxiv' in bib_entry.fields['journal'].lower():
        field_text = tex_journal

    elif tex_journal in journal_transform.keys():
        field_text = journal_transform[tex_journal]

    else:
        field_text = tex_journal

    return field_text


def format_reference(bib_entry, Nshow=3, Nmax=8):
    # Handle different entry types:
    bibitem = bib_entry.fields
    if bib_entry.type.lower() == 'article':
        # author year, journal, volume, pages
        year = bibitem['year']
        author = format_author_list(bib_entry, Nshow, Nmax)
        if 'pages' in bibitem.keys():
            journal = format_journal_name(bib_entry)
            pages = bibitem['pages']
            volume = bibitem['volume']
            if '-' in pages:
                pages = pages.split('-')[0]

            ref = u"{} {}, {}, {}, {}".format(author, year, journal, volume, pages)

        else:
            if 'arxiv' in bibitem['journal'].lower():
                arXivID = 'arXiv:' + bibitem['eprint']
                ref = u"{} {}, {}".format(author, year, arXivID)

            else:
                if bibitem['journal'] in journal_transform.keys():
                    journal = format_journal_name(bib_entry)
                else:
                    journal = bibitem['journal']
                ref = u"{} {}, {}".format(author, year, journal)

    elif bib_entry.type.lower() == 'inproceedings':
        author = format_author_list(bib_entry, Nshow, Nmax)
        year = bibitem['year']
        title = clean_string(bibitem['title'].replace('\n', ' '))
        booktitle = clean_string(bibitem['booktitle'])
        if 'journal' in bibitem.keys() and 'volume' in bibitem.keys():
            journal = bibitem['journal']
            volume = bibitem['volume']
            biblist = (author, year, title, journal, volume, booktitle)
            ref = u"{} ({}), `{}'. In {} {}, {}".format(*biblist)

        elif 'editor' in bibitem.keys():
            editor, editor_numerator = format_editor_list(bib_entry)

            biblist = (author, year, title, editor, booktitle)
            ref = u"{} ({}), {}. In {} {}, {}".format(*biblist)

    elif bib_entry.type.lower() == 'inbook':
        if 'author' in bibitem.keys():
            author = format_author_list(bib_entry, Nshow, Nmax)
        elif 'editor' in bibitem.keys():
            author, _ = format_editor_list(bib_entry)
        year = bibitem['year']
        title = clean_string(bibitem['title'].replace('\n', ' '))
        publisher = bibitem['publisher']
        if 'pages' in bibitem.keys():
            pages = 'pp. ' + bibitem['pages']

        biblist = (author, year, title, publisher)
        ref = u"{} {}, `{}': {}".format(*biblist)

    elif bib_entry.type.lower() == 'phdthesis':
        year = bibitem['year']
        title = clean_string(bibitem['title'].replace('\n', ' '))
        author = format_author_list(bib_entry, Nshow, Nmax)
        school = clean_string(bibitem['school'])

        ref = u"{} {}, PhD thesis, {}".format(author, year, school)

    else:
        ref = u"Reference format not defined for type: " + bib_entry.type
        print u"\n  Reference format is not defined for type: " + bib_entry.type
        print u"  Add definition in function 'bibtex.format_reference'\n"

    return ref


def format_author_name(name_dict):
    """
    Input expected is a dictionary containing a full name in BibTeX style, e.g.:
     {'first': [u'J.-K.'],
      'last': [u'Krogager'],
      'jr': [],
      'von': []
     }
    Returns: BibTeX formatted author string.
    """
    surname = ' '.join(name_dict['von'] + name_dict['last'])
    firstname = '~'.join(name_dict['first'])
    jr = ' '.join(name_dict['jr'])

    if '{' in surname and '}' in surname:
        use_brackets = False
    else:
        use_brackets = True

    if jr:
        if use_brackets:
            output_format = "{%s}, %s, %s"
        else:
            output_format = "%s, %s, %s"
        output = (surname, jr, firstname)
    else:
        if use_brackets:
            output_format = "{%s}, %s"
        else:
            output_format = "%s, %s"
        output = (surname, firstname)

    return output_format % output


# Following definitions are taken from

class InvalidName(ValueError):
    """Exception raised by :py:func:`customization.splitname` when an invalid name is input.
    """
    pass


def splitname(name, strict_mode=True):
    """
    Break a name into its constituent parts: First, von, Last, and Jr.
    :param string name: a string containing a single name
    :param Boolean strict_mode: whether to use strict mode
    :returns: dictionary of constituent parts
    :raises `customization.InvalidName`: If an invalid name is given and
                                         ``strict_mode = True``.
    In BibTeX, a name can be represented in any of three forms:
        * First von Last
        * von Last, First
        * von Last, Jr, First
    This function attempts to split a given name into its four parts. The
    returned dictionary has keys of ``first``, ``last``, ``von`` and ``jr``.
    Each value is a list of the words making up that part; this may be an empty
    list.  If the input has no non-whitespace characters, a blank dictionary is
    returned.
    It is capable of detecting some errors with the input name. If the
    ``strict_mode`` parameter is ``True``, which is the default, this results in
    a :class:`customization.InvalidName` exception being raised. If it is
    ``False``, the function continues, working around the error as best it can.
    The errors that can be detected are listed below along with the handling
    for non-strict mode:
        * Name finishes with a trailing comma: delete the comma
        * Too many parts (e.g., von Last, Jr, First, Error): merge extra parts
          into First
        * Unterminated opening brace: add closing brace to end of input
        * Unmatched closing brace: add opening brace at start of word
    """
    # Useful references:
    # http://maverick.inria.fr/~Xavier.Decoret/resources/xdkbibtex/bibtex_summary.html#names
    # http://tug.ctan.org/info/bibtex/tamethebeast/ttb_en.pdf

    # Whitespace characters that can separate words.
    whitespace = set(' ~\r\n\t')

    # We'll iterate over the input once, dividing it into a list of words for
    # each comma-separated section. We'll also calculate the case of each word
    # as we work.
    sections = [[]]      # Sections of the name.
    cases = [[]]         # 1 = uppercase, 0 = lowercase, -1 = caseless.
    word = []            # Current word.
    case = -1            # Case of the current word.
    level = 0            # Current brace level.
    bracestart = False   # Will the next character be the first within a brace?
    controlseq = True    # Are we currently processing a control sequence?
    specialchar = None   # Are we currently processing a special character?

    # Using an iterator allows us to deal with escapes in a simple manner.
    nameiter = iter(name)
    for char in nameiter:
        # An escape.
        if char == '\\':
            escaped = next(nameiter)

            # BibTeX doesn't allow whitespace escaping. Copy the slash and fall
            # through to the normal case to handle the whitespace.
            if escaped in whitespace:
                word.append(char)
                char = escaped

            else:
                # Is this the first character in a brace?
                if bracestart:
                    bracestart = False
                    controlseq = escaped.isalpha()
                    specialchar = True

                # Can we use it to determine the case?
                elif (case == -1) and escaped.isalpha():
                    if escaped.isupper():
                        case = 1
                    else:
                        case = 0

                # Copy the escape to the current word and go to the next
                # character in the input.
                word.append(char)
                word.append(escaped)
                continue

        # Start of a braced expression.
        if char == '{':
            level += 1
            word.append(char)
            bracestart = True
            controlseq = False
            specialchar = False
            continue

        # All the below cases imply this (and don't test its previous value).
        bracestart = False

        # End of a braced expression.
        if char == '}':
            # Check and reduce the level.
            if level:
                level -= 1
            else:
                if strict_mode:
                    raise InvalidName("Unmatched closing brace in name {{{0}}}.".format(name))
                word.insert(0, '{')

            # Update the state, append the character, and move on.
            controlseq = False
            specialchar = False
            word.append(char)
            continue

        # Inside a braced expression.
        if level:
            # Is this the end of a control sequence?
            if controlseq:
                if not char.isalpha():
                    controlseq = False

            # If it's a special character, can we use it for a case?
            elif specialchar:
                if (case == -1) and char.isalpha():
                    if char.isupper():
                        case = 1
                    else:
                        case = 0

            # Append the character and move on.
            word.append(char)
            continue

        # End of a word.
        # NB. we know we're not in a brace here due to the previous case.
        if char == ',' or char in whitespace:
            # Don't add empty words due to repeated whitespace.
            if word:
                sections[-1].append(''.join(word))
                word = []
                cases[-1].append(case)
                case = -1
                controlseq = False
                specialchar = False

            # End of a section.
            if char == ',':
                if len(sections) < 3:
                    sections.append([])
                    cases.append([])
                elif strict_mode:
                    raise InvalidName("Too many commas in the name {{{0}}}.".format(name))
            continue

        # Regular character.
        word.append(char)
        if (case == -1) and char.isalpha():
            if char.isupper():
                case = 1
            else:
                case = 0

    # Unterminated brace?
    if level:
        if strict_mode:
            raise InvalidName("Unterminated opening brace in the name {{{0}}}.".format(name))
        while level:
            word.append('}')
            level -= 1

    # Handle the final word.
    if word:
        sections[-1].append(''.join(word))
        cases[-1].append(case)

    # Get rid of trailing sections.
    if not sections[-1]:
        # Trailing comma?
        if (len(sections) > 1) and strict_mode:
            raise InvalidName("Trailing comma at end of name {{{0}}}.".format(name))
        sections.pop(-1)
        cases.pop(-1)

    # No non-whitespace input.
    if not sections or not any(bool(section) for section in sections):
        return {}

    # Initialise the output dictionary.
    parts = {'first': [], 'last': [], 'von': [], 'jr': []}

    # Form 1: "First von Last"
    if len(sections) == 1:
        p0 = sections[0]

        # One word only: last cannot be empty.
        if len(p0) == 1:
            parts['last'] = p0

        # Two words: must be first and last.
        elif len(p0) == 2:
            parts['first'] = p0[:1]
            parts['last'] = p0[1:]

        # Need to use the cases to figure it out.
        else:
            cases = cases[0]

            # First is the longest sequence of words starting with uppercase
            # that is not the whole string. von is then the longest sequence
            # whose last word starts with lowercase that is not the whole
            # string. Last is the rest. NB., this means last cannot be empty.

            # At least one lowercase letter.
            if 0 in cases:
                # Index from end of list of first and last lowercase word.
                firstl = cases.index(0) - len(cases)
                lastl = -cases[::-1].index(0) - 1
                if lastl == -1:
                    lastl -= 1      # Cannot consume the rest of the string.

                # Pull the parts out.
                parts['first'] = p0[:firstl]
                parts['von'] = p0[firstl:lastl + 1]
                parts['last'] = p0[lastl + 1:]

            # No lowercase: last is the last word, first is everything else.
            else:
                parts['first'] = p0[:-1]
                parts['last'] = p0[-1:]

    # Form 2 ("von Last, First") or 3 ("von Last, jr, First")
    else:
        # As long as there is content in the first name partition, use it as-is.
        first = sections[-1]
        if first and first[0]:
            parts['first'] = first

        # And again with the jr part.
        if len(sections) == 3:
            jr = sections[-2]
            if jr and jr[0]:
                parts['jr'] = jr

        # Last name cannot be empty; if there is only one word in the first
        # partition, we have to use it for the last name.
        last = sections[0]
        if len(last) == 1:
            parts['last'] = last

        # Have to look at the cases to figure it out.
        else:
            lcases = cases[0]

            # At least one lowercase: von is the longest sequence of whitespace
            # separated words whose last word does not start with an uppercase
            # word, and last is the rest.
            if 0 in lcases:
                split = len(lcases) - lcases[::-1].index(0)
                if split == len(lcases):
                    split = 0            # Last cannot be empty.
                parts['von'] = sections[0][:split]
                parts['last'] = sections[0][split:]

            # All uppercase => all last.
            else:
                parts['last'] = sections[0]

    # Done.
    return parts
