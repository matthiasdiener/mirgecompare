def compare_files_vtu(first_file, second_file, file_type, tolerance = 1e-12):
    import vtk

    # read files: EXTEND TO OTHER FILE TYPES IN FUTURE
    if file_type == "vtu":
        reader1 = vtk.vtkXMLUnstructuredGridReader()
        reader2 = vtk.vtkXMLUnstructuredGridReader()
    elif file_type == "pvtu":
        reader1 = vtk.vtkXMLPUnstructuredGridReader()
        reader2 = vtk.vtkXMLPUnstructuredGridReader()
    else:
        # print("File type not supported")
        raise ValueError("File type not supported")

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

if __name__ == "__main__":
    import argparse

    # read in file and comparison info from command line
    parser = argparse.ArgumentParser(description = 'Process files to perform fidelity check')
    parser.add_argument('files', nargs = 2, type = str)
    parser.add_argument('file_type', type = str)
    parser.add_argument('--tolerance', type = float)
    args = parser.parse_args();

    first_file = args.files[0]  # for testing: fld-wave-eager-0000.vtu, autoignition-000000.pvtu
    second_file = args.files[1] # for testing: autoignition-000000-0001.vtu, fld-wave-eager-mpi-000-0000.pvtu
    # TODO: change file paths to match actual mirgecom output directory later ?
    first_file = "examples/" + first_file
    second_file = "examples/" + second_file

    file_type = args.file_type

    user_tolerance = 1e-12
    if args.tolerance:
        user_tolerance = args.tolerance

    # call comparison function to run fidelity check on given files
    compare_files_vtu(first_file, second_file, file_type, user_tolerance)
