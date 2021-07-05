def compare_files_vtu(first_file, second_file, file_type, tolerance = 1e-12):
    import vtk

    # read files:
    if file_type == "vtu":
        reader1 = vtk.vtkXMLUnstructuredGridReader()
        reader2 = vtk.vtkXMLUnstructuredGridReader()
    else:
        reader1 = vtk.vtkXMLPUnstructuredGridReader()
        reader2 = vtk.vtkXMLPUnstructuredGridReader()

    reader1.SetFileName(first_file)
    reader1.Update()
    output1 = reader1.GetOutput()

    reader2.SetFileName(second_file)
    reader2.Update()
    output2 = reader2.GetOutput()

    # check fidelity
    point_data1 = output1.GetPointData()
    point_data2 = output2.GetPointData()

    # verify same number of PointData arrays in both files
    if point_data1.GetNumberOfArrays() != point_data2.GetNumberOfArrays():
        print("File 1:", point_data1.GetNumberOfArrays(), "\n", "File 2:", point_data2.GetNumberOfArrays())
        raise ValueError("Fidelity test failed: Mismatched data array count")

    for i in range(point_data1.GetNumberOfArrays()):
        arr1 = point_data1.GetArray(i)
        arr2 = point_data2.GetArray(i)

        # verify both files contain same arrays
        if point_data1.GetArrayName(i) != point_data2.GetArrayName(i):
            print("File 1:", point_data1.GetArrayName(i), "\n", "File 2:", point_data2.GetArrayName(i))
            raise ValueError("Fidelity test failed: Mismatched data array names")

        # verify arrays are same sizes in both files
        if arr1.GetSize() != arr2.GetSize():
            print("File 1, DataArray", i, ":", arr1.GetSize(), "\n", "File 2, DataArray", i, ":", arr2.GetSize())
            raise ValueError("Fidelity test failed: Mismatched data array sizes")

        # verify individual values w/in given tolerance
        for j in range(arr1.GetSize()):
            if (arr1.GetValue(j) - arr2.GetValue(j)) > tolerance: 
                print("Tolerance:", tolerance)
                raise ValueError("Fidelity test failed: Mismatched data array values with given tolerance")

    print("Fidelity test completed successfully with tolerance", tolerance)

class XdmfReader():
    def __init__(self, filename): 
        import xml.etree.ElementTree as ET

        tree = ET.parse(filename)
        root = tree.getroot()

        domains = tuple(root)
        self.domain = domains[0]
        # TODO: add functionality for multiple grids/grid types ?
        self.grids = tuple(self.domain)
        self.uniform_grid = self.grids[0]

    def get_topology(self):
        connectivity = None

        for a in self.uniform_grid:
            if a.tag == "Topology":
                connectivity = a

        # TODO: what kind of error is appropriate to raise here?
        if connectivity == None:
            raise ValueError("File is missing grid connectivity data") 

        return connectivity

    def get_geometry(self):
        geometry = None

        for a in self.uniform_grid:
            if a.tag == "Geometry":
                geometry = a
        
        # TODO: what kind of error is appropriate to raise here?
        if geometry == None:
            raise ValueError("File is missing grid node location data") 

        return geometry
    
    def read_data_item(self, data_item):
        # CURRENTLY DOES NOT SUPPORT 'DataItem' THAT STORES VALUES DIRECTLY

        # check that data stored as separate hdf5 file
        if data_item.get("Format") != "HDF":
            raise TypeError("Data stored in unrecognized format")
        
        # get corresponding hdf5 file
        source_info = data_item.text
        split_source_info = source_info.partition(":")

        h5_filename = split_source_info[0]
        # TODO: change file name to match actual mirgecom output directory later ?
        h5_filename = "examples/" + h5_filename
        h5_datapath = split_source_info[2]

        # read data from corresponding hdf5 file
        import h5py

        f = h5py.File(h5_filename, 'r')
        source_data = f[h5_datapath]

        return source_data

def compare_files_xdmf(first_file, second_file, tolerance = 1e-12):
    # TODO: write xdmf comparison w/ XdmfReader

    # compare Topology [same TopologyType, same # of values, values w/in tolerance]

    # compare Geometry [same GeometryType, same # of values, values w/in tolerance]

    # compare other Attributes [same number of extra attributes, same AttributeType, same name, same # of values, values w/in tolerance]

    print("Fidelity test completed successfully with tolerance", tolerance)

# run fidelity check
if __name__ == "__main__":
    import argparse

    # read in file and comparison info from command line
    parser = argparse.ArgumentParser(description = 'Process files to perform fidelity check')
    parser.add_argument('files', nargs = 2, type = str)
    parser.add_argument('file_type', type = str)
    parser.add_argument('--tolerance', type = float)
    args = parser.parse_args();

    first_file = args.files[0]  # for testing: fld-wave-eager-0000.vtu, autoignition-000000.pvtu, visualizer_xdmf_box_2d.xmf
    second_file = args.files[1] # for testing: autoignition-000000-0001.vtu, fld-wave-eager-mpi-000-0000.pvtu, visualizer_xdmf_simplex_2d.xmf
    # TODO: change file paths to match actual mirgecom output directory later ?
    first_file = "examples/" + first_file
    second_file = "examples/" + second_file

    file_type = args.file_type

    user_tolerance = 1e-12
    if args.tolerance:
        user_tolerance = args.tolerance

    # EXTEND TO MORE FILE TYPES IN FUTURE
    # use appropriate comparison function for file type
    if file_type == "vtu" or "pvtu":
        compare_files_vtu(first_file, second_file, file_type, user_tolerance)
    elif file_type == "xdmf" or "xmf":
        compare_files_xdmf(first_file, second_file, user_tolerance)
    else:
        raise TypeError()("File type not supported")
