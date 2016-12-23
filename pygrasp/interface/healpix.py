import numpy
import healpy

import grasp_io

def field_directions_from_healpix( nside, max_tht ):
  
  filename = 'nside%06d_tht=%4f.sta' % (nside, max_tht)
  
  max_tht = numpy.radians(max_tht)
  
  npix = healpy.query_disc( nside, (0,0,1), max_tht ).size
  
  pixels = numpy.arange(0,npix)
  
  tht,phi = healpy.pix2ang( nside, pixels )
  
  grasp_io.gen_field_directions( tht,phi, filename )
  