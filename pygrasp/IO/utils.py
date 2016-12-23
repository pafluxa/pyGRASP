import pandas
import numpy
from numpy import cos,sin

def get_grid_metadata( filename ):
	"""
	Returns a dictionary with GRASP grid metadata without reading the whole file.
	"""
  
	f = open( filename, 'r' )
	
	# Read header
	mdata = {}
	header = ""
	line = f.readline()
	while "++++" not in line[0:4]:
		header = header + line
		line   = f.readline()
		
	ktype = map( int, f.readline().strip() )
	
	nset,icomp,ncomp,igrid = map(int, f.readline().strip().split())
	
	mdata['header'] = header
	mdata[  'nset'] = nset
	mdata[ 'icomp'] = icomp
	mdata[ 'ncomp'] = ncomp
	mdata[ 'igrid'] = igrid
	
	# Read set metadata
	set_mdata = []
	for i in range(0,nset):
	
		ix,iy = map(int, f.readline().strip().split())
		set_mdata.append( {'ix':ix, 'iy':iy } )
		
	for s in set_mdata:
	
		xs,ys,xe,ye  = map(float, f.readline().strip().split())
		nx,ny,klimit = map(int  , f.readline().strip().split())
		
		if klimit == 0:
			_is = 1
			ie  = nx
			# jump to next metadata block
			for l in range(0,nx*ny):
				l = f.readline()
		
		elif klimit == 1:
			raise ValueError, '\
			Reading this GRASP grid file is unsupported.\
			Try recalculating the field using rectangular\
			limits for your grid.'
		
		s['limits'] = (xs,xe,ys,ye)
		s['nx']     = nx
		s['ny']     = ny
	
	f.close()
	
	return mdata, set_mdata

def get_grid_data( filename ):
	"""
    Returns a list of numpy tables containing electric field data from a grasp grid
    and its corresponding metadata.
	"""
  
	gridMD, setMD = get_grid_metadata( filename )
	
	ncomp = gridMD['ncomp']
	icomp = gridMD['icomp']
	
	# Create names from icomp ncomp
	dtypes = {}
	names  = None
	if ncomp == 2:

		if icomp == 1:
			names = ('RE_E_tht', 'IM_E_tht', 
			         'RE_E_phi', 'IM_E_phi' )
		elif icomp == 2:
			names = ('RE_E_rhc', 'IM_E_lhc', 
			         'RE_E_rhc', 'IM_E_lhc' )
		elif icomp == 3:
			names = ('RE_E_co', 'IM_E_co', 
			         'RE_E_cx', 'IM_E_cx' )
		elif icomp == 4:
			names = ('RE_E_maj', 'IM_E_maj', 
			         'RE_E_min', 'IM_E_min' )
		elif icomp == 9:
			names = ('RE_E_pwr', 'IM_E_pwr', 
			         'RE_E_prt', 'IM_E_prt' )	
		else:
			raise ValueError, 'unsupported grid data.'		
	
	if ncomp == 3:
		if icomp == 1:
			names = ('RE_E_tht' , 'IM_E_tht', 
			         'RE_E_phi' , 'IM_E_phi',
			         'RE_Ez_phi', 'IM_Ez_phi' )
		elif icomp == 2:
			names = ('RE_E_rhc' , 'IM_E_lhc', 
			         'RE_E_rhc' , 'IM_E_lhc',
			         'RE_Ez_rhc', 'IM_Ez_lhc' )
		elif icomp == 3:
			names = ('RE_E_co'  , 'IM_E_co', 
			         'RE_E_cx'  , 'IM_E_cx',
			         'RE_Ez_r'  , 'IM_Ez_r' )
		elif icomp == 4:
			names = ('RE_E_maj' , 'IM_E_maj', 
			         'RE_E_min' , 'IM_E_min',
			         'RE_Ez_min', 'IM_Ez_min' )
		elif icomp == 9:
			names = ('RE_E_pwr' , 'IM_E_pwr', 
			         'RE_E_prt' , 'IM_E_prt',
			         'RE_Ez_prt', 'IM_Ez_prt' )	
		else:
			raise ValueError, 'unsupported grid data.'
	
	for n in names:
			dtypes.update( {n : numpy.float64} )
			
	# Add the extra lines from set grid metadata
	skipLines = gridMD['header'].count('\n') + 1 + 1 + 1 + gridMD['nset'] + 2
	
	# Data is a list of 'nset' datasets
	data = []
	for s in range( gridMD['nset'] ):
	#for s in range( 2 ):
	  
		d = pandas.read_table( 
			filename,
			engine='c',
			skiprows=skipLines,
			nrows=setMD[s]['nx']*setMD[s]['ny'],
			header=None,
			names=names,
			index_col=False,
			dtype=dtypes ,
			delim_whitespace=True,
			skipinitialspace=True,
			verbose=False)
					
		skipLines += setMD[s]['nx']*setMD[s]['ny'] + 2
		
		print 'read set ', s
		
		data.append( d )
		
	return data
	"""  
	f = open( filename, 'r' )
	# Read header
	mdata = {}
	set_mdata = []
	data = []
	data_block_lines = []
	
	curr_line = 0
	header = ""
	line = f.readline()
	curr_line += 1
	while "++++" not in line[0:4]:
	header = header + line
	line   = f.readline()
	curr_line += 1
	
	ktype = map( int, f.readline().strip() )
	curr_line += 1
	nset,icomp,ncomp,igrid = map(int, f.readline().strip().split())
	curr_line += 1
	
	mdata['header'] = header
	mdata['nset'] = nset
	mdata['icomp'] = icomp
	mdata['ncomp'] = ncomp
	mdata['igrid'] = igrid
	
	for i in range(0,nset):
	ix,iy = map(int, f.readline().strip().split())
	curr_line += 1
	set_mdata.append( {'ix':ix, 'iy':iy } )
	
	for s in set_mdata:
	xs,ys,xe,ye  = map(float, f.readline().strip().split())
	curr_line += 1
	
	nx,ny,klimit = map(int  , f.readline().strip().split())
	curr_line += 1
	
	if klimit == 0:
	_is = 1
	ie  = nx
	data_block_lines.append( curr_line )
	#skip data
	for l in range(0,nx*ny):
	l = f.readline()
	curr_line += 1
	
	if klimit == 1:
	raise ValueError, 'Reading this GRASP grid file is unsupported. Try recalculating the field using rectangular limits for your grid.'
	
	f.close()
	
	# load data
	for data_block_start in data_block_lines:
	
	if ncomp == 2:
	r1,i1,r2,i2 = numpy.genfromtxt( filename, dtype=numpy.float, skip_header=data_block_start, max_rows=nx*ny, unpack=True )
	r3,i3 = r1*0, i1*0
	data.append( numpy.asarray( (r1+1.j*i1,r2+1.j*i2,r3+1.j*i3) ) ) 
	
	if ncomp == 3:
	r1,i1,r2,i2,r3,i3 = numpy.genfromtxt( filename, dtype=numpy.float, skip_header=data_block_start, max_rows=nx*ny, unpack=True )
	data.append( numpy.asarray( (r1+1.j*i1,r2+1.j*i2,r3+1.j*i3) ) ) 
	
	s['limits'] = (xs,xe,ys,ye)
	s['nx'] = nx
	s['ny'] = ny
	
	return mdata, set_mdata, data
	"""
  
def get_tabulated_field_data( filename ):
  """
    Returns numpy array with far-field values for specified directions.
    See GRASP user's manual (page 1067 for version 10.3)
  """
  
  data = []
  
  counter = 0
  f = open( filename, 'r' )
  
  title = f.readline().strip()
  counter += 1
  
  nsets,nparts = map( int, f.readline().strip().split() )
  counter +=1 
  
  for s in range(0,nsets):
    for p in range(0,nparts):
      
      npoints     = (int)( f.readline().strip() )
      ibeam       = f.readline().strip()
      
      ibeam       = (int)( ibeam )
      counter    += 2
      
      r1,i1,r2,i2 = numpy.genfromtxt( filename, dtype=numpy.float, skip_header=counter, max_rows=npoints, unpack=True )
      
      data.append( numpy.asarray( (r1+1.j*i1,r2+1.j*i2) ) )
      
      counter += npoints
  
  return data
      
def gen_field_directions( tht, phi, filename, component='co', rot=None ):  
  """
    Creates a file with tabulated field directions in GRASP format.
  
    component : 'co' means co-polar
                'cx' means cross-polar
                     
    rot : array of tht.size with point wise rotations respect to field coordinate system.
  """
  
  if numpy.max(tht) > numpy.pi or numpy.min(tht) < 0:
    raise ValueError, 'tht out of range'
  
  if numpy.max( phi ) > 2*numpy.pi or numpy.min( phi ) < 0:
    raise ValueError, 'phi out of range'
  
  f = open( filename, 'w' )
  
  f.write( "%4.6f\n" % (tht.size) )
  
  ipol = 0
  if component == 'co':
    ipol = 1
  elif component == 'cx':
    ipol = 2
  else:
    raise ValueError, 'Please provide a component, either co or cx'
 
  if rot == None:
    rot = 0*tht
  
  u = cos(phi)*sin(tht)
  v = sin(phi)*sin(tht)
  
  for _u,_v,_rot in zip(u,v,rot):
    line = "%1.10E %1.10E 0 0 %2d %1.10E 0 0\n" % (_u,_v, ipol, _rot)
    f.write(line)
  
  f.write( '0\n' )
  
  f.close()
    
