import vtk

# TODO: convert to command line args
# read in files names
first_file = input("Enter first file name: ") # for testing: fld-wave-eager-0000.vtu, autoignition-000000.pvtu
second_file = input("Enter second file name: ") # for testing: autoignition-000000-0001.vtu, fld-wave-eager-mpi-000-0000.pvtu
# TODO: change file paths to match actual mirgecom output directory later ?
first_file = "examples/" + first_file
second_file = "examples/" + second_file

# read in tolerance value
user_tolerance = input("Enter desired comparison tolerance value (default = 1e-12): ")

# read in file type: EXTEND TO OTHER FILE TYPES IN FUTURE
file_type = input("Enter file type of comparison [vtu, pvtu]: ")

# function comparing fidelity of given files
def compare_files(first_file, second_file, file_type, tolerance = 1e-12):
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

    print("Fidelity test completed successfully.")

# call comparison function to run fidelity check on given files
compare_files(first_file, second_file, file_type, user_tolerance)
