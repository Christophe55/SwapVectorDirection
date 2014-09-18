# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SwapVectorDirection
                                 A QGIS plugin
 Swap Vector Direction permet d'inverser la direction d'un vecteur
                             -------------------
        begin                : 2014-09-17
        copyright            : (C) 2014 by Christophe Maginot
        email                : christophe.maginot@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SwapVectorDirection class from file SwapVectorDirection.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .SwapVectorDirection import SwapVectorDirection
    return SwapVectorDirection(iface)
