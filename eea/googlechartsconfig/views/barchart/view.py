# -*- coding: utf-8 -*-
""" BarChart View
"""
__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'
__credits__ = """contributions: Zoltan Szabo"""

import json
import urllib

from zope.interface import implements
from zope.component import queryAdapter
from zope.annotation.interfaces import IAnnotations

from eea.googlechartsconfig.interfaces import IGoogleChartConfig
from eea.daviz.interfaces import IDavizConfig
from eea.googlechartsconfig.views.view import ViewForm
from eea.googlechartsconfig.views.barchart.interfaces import IGoogleChartBarChart
from eea.googlechartsconfig.config import ANNO_VIEWS, ANNO_FACETS, ANNO_JSON, ANNO_SOURCES
from eea.googlechartsconfig.converter.exhibit2googlechart import exhibit2googlechart

class View(ViewForm):
    """ BarChartView
    """
    label = 'BarChart'
    implements(IGoogleChartBarChart)

    @property
    def details(self):
        """ Show details column?
        """
        return self.data.get('details', False)

    @property
    def columns(self):
        """ Returns columns property for view1
        """
        columns = self.data.get('columns', [])
        for column in columns:
            yield '.%s' % column

        if self.details:
            yield '!label'

    @property
    def formats(self):
        """ Column formats
        """
        accessor = queryAdapter(self.context, IDavizConfig)
        columns = self.data.get('columns', [])
        for column in columns:
            facet = accessor.facet(column, {})
            itype = facet.get('item_type', 'text')
            yield itype

        if self.details:
            yield "item {title: expression('more')}"

    @property
    def labels(self):
        """ Returns labels property for view1
        """
        accessor = queryAdapter(self.context, IDavizConfig)
        columns = self.data.get('columns', [])

        for column in columns:
            facet = accessor.facet(column, {})
            label = facet.get('label', column)
            yield label

        if self.details:
            yield 'Details'

    def settingsAndData(self):
        columns = []
        facets = {}
        accessor = queryAdapter(self.context, IDavizConfig)
        acc_settings = [view for view in accessor.views if view['name'] == 'googlechart.charts'][0]

        for facet in accessor.facets:
            facets[facet['name']] = facet['label']
        for column in acc_settings.get('columns'):
            columns.append([column, facets[column]])

        result = json.load(urllib.urlopen(self.context.absolute_url()+'/@@daviz-view.json'))
        dataTable = exhibit2googlechart(result, columns)

        settings = {}
        chart_type = acc_settings.get('chartType', [])
        chart_type = chart_type.pop() if chart_type else ''
        settings["chartType"] = "ImageChart" if chart_type == "ImageChart" else "BarChart"
        options = {}
        vAxis = {}
        vAxis["title"] = acc_settings.get('verticalTitle', 'Vertical Title')
        titleTextStyle={}
        titleTextStyle["color"] = "red"
        hAxis = {}
        vAxis["titleTextStyle"] = titleTextStyle
        hAxis["title"] = acc_settings.get('horizontalTitle', 'Horizontal Title')
        options["hAxis"] = hAxis
        options["vAxis"] = vAxis
        options["title"] = acc_settings.get('chartTitle', 'Chart Title')
        options["width"] = "500"
        settings["options"] = options

        settings["dataTable"] = dataTable
        return json.dumps(settings)

