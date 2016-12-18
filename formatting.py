# -*- coding: UTF-8 -*-

"""
    Formatting tools for BibTeX data
    A 'bib_entry' refers to a 'Entry' instance of pybtex database.
"""

# from pylatexenc import latexencode
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


all_bibtex_fields = [
    'author',
    'title',
    'journal',
    'volume',
    'pages',
    'year',
    'month',
    'number',
    'series',
    'note',
    'booktitle',
    'chapter',
    'crossref',
    'editor',
    'edition',
    'institution',
    'publisher',
    'school',
    'organization',
    'address',
    'annote',
    'howpublished'
]


def unicode_char_in_string(string):
    try:
        string.encode('ascii')
        return False

    except UnicodeEncodeError:
        return True


def format_editor_list(bib_entry):
    """ Format the list of editors. """
    bibitem = bib_entry.fields
    editor_list = bibitem['editor'].split(' and ')
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

    author_list = bib_entry.fields['author'].split(' and ')
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
