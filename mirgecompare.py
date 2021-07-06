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
            if abs(arr1.GetValue(j) - arr2.GetValue(j)) > tolerance: 
                print("Tolerance:", tolerance)
                raise ValueError("Fidelity test failed: Mismatched data array values with given tolerance")

    print("VTU Fidelity test completed successfully with tolerance", tolerance)

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
    # read files
    file_reader1 = XdmfReader(first_file)
    file_reader2 = XdmfReader(second_file)

    # check same number of grids
    if len(file_reader1.grids) != len(file_reader2.grids):
        print("File 1:", len(file_reader1.grids), "\n", "File 2:", len(file_reader2.grids))
        raise ValueError("Fidelity test failed: Mismatched grid count")
    
    # check same number of cells in grid
    if len(file_reader1.uniform_grid) != len(file_reader2.uniform_grid):
        print("File 1:", len(file_reader1.uniform_grid), "\n", "File 2:", len(file_reader2.uniform_grid))
        raise ValueError("Fidelity test failed: Mismatched cell count in uniform grid")

    # compare Topology: 
    top1 = file_reader1.get_topology()
    top2 = file_reader2.get_topology()

    # check TopologyType
    if top1.get("TopologyType") != top2.get("TopologyType"):
        print("File 1:", top1.get("TopologyType"), "\n", "File 2:", top2.get("TopologyType"))
        raise ValueError("Fidelity test failed: Mismatched topology type")
    
    # check number of connectivity values
    connectivities1 = file_reader1.read_data_item(tuple(top1)[0])
    connectivities2 = file_reader2.read_data_item(tuple(top2)[0])

    if len(connectivities1) != len(connectivities2):
        print("File 1:", len(connectivities1), "\n", "File 2:", len(connectivities2))
        raise ValueError("Fidelity test failed: Mismatched connectivities count")

    # check connectivity values w/in tolerance
    for i in range(len(connectivities1)):
        for j in range(len(connectivities1[i])):
            if abs(connectivities1[i][j] - connectivities2[i][j]) > int(tolerance):
                print("Tolerance:", tolerance)
                raise ValueError("Fidelity test failed: Mismatched connectivity values with given tolerance")

    # compare Geometry:
    geo1 = file_reader1.get_geometry()
    geo2 = file_reader2.get_geometry()

    # check GeometryType
    if geo1.get("GeometryType") != geo2.get("GeometryType"):
        print("File 1:", geo1.get("GeometryType"), "\n", "File 2:", geo2.get("GeometryType"))
        raise ValueError("Fidelity test failed: Mismatched geometry type")

    # check number of node values
    nodes1 = file_reader1.read_data_item(tuple(geo1)[0])
    nodes2 = file_reader2.read_data_item(tuple(geo2)[0])

    if len(nodes1) != len(nodes2):
        print("File 1:", len(nodes1), "\n", "File 2:", len(nodes2))
        raise ValueError("Fidelity test failed: Mismatched nodes count")

    # check node values w/in tolerance
    for i in range(len(nodes1)):
        for j in range(len(nodes1[i])):
            if abs(nodes1[i][j] - nodes2[i][j]) > tolerance:
                print("Tolerance:", tolerance)
                raise ValueError("Fidelity test failed: Mismatched node values with given tolerance")

    # compare other Attributes:
    for i in range(len(file_reader1.uniform_grid)):
        curr_cell1 = file_reader1.uniform_grid[i]
        curr_cell2 = file_reader2.uniform_grid[i]

        # skip already checked cells
        if curr_cell1.tag == "Geometry" or curr_cell1.tag == "Topology":
            continue

        # check AttributeType
        if curr_cell1.get("AttributeType") != curr_cell2.get("AttributeType"):
            print("File 1:", curr_cell1.get("AttributeType"), "\n", "File 2:", curr_cell2.get("AttributeType"))
            raise ValueError("Fidelity test failed: Mismatched cell type")

        # check Attribtue name
        if curr_cell1.get("Name") != curr_cell2.get("Name"):
            print("File 1:", curr_cell1.get("Name"), "\n", "File 2:", curr_cell2.get("Name"))
            raise ValueError("Fidelity test failed: Mismatched cell name")

        # check number of Attribute values
        values1 = file_reader1.read_data_item(tuple(curr_cell1)[0])
        values2 = file_reader2.read_data_item(tuple(curr_cell2)[0])

        if len(values1) != len(values2):
            print("File 1,", curr_cell1.get("Name"), ":", len(values1), "\n", "File 2,", curr_cell2.get("Name"), ":", len(values2))
            raise ValueError("Fidelity test failed: Mismatched data values count")

        # check values w/in tolerance
        for i in range(len(values1)):
            if abs(values1[i] - values2[i]) > tolerance:
                print("Tolerance:", tolerance, "\n", "Cell:", curr_cell1.get("Name"))
                raise ValueError("Fidelity test failed: Mismatched data values with given tolerance")

    print("XDMF Fidelity test completed successfully with tolerance", tolerance)

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
    if file_type == "vtu" or file_type == "pvtu":
        compare_files_vtu(first_file, second_file, file_type, user_tolerance)
    elif file_type == "xdmf" or file_type == "xmf":
        compare_files_xdmf(first_file, second_file, user_tolerance)
    else:
        raise TypeError()("File type not supported")
