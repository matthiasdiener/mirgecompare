import vtk

CONST_TOLERANCE = 1e-12

# TODO: convert to command line args?
# read in file names to compare: 
first_file = input("Enter first file name: ") # for testing: fld-wave-eager-0000.vtu, autoignition-000000.pvtu
second_file = input("Enter second file name: ") # for testing: autoignition-000000-0001.vtu, fld-wave-eager-mpi-000-0000.pvtu
# TODO: change file paths to match actual mirgecom output directory later ?
first_file = "examples/" + first_file
second_file = "examples/" + second_file

# set file type to compare
file_type = "vtu"
if first_file[-4:] == "pvtu":
    file_type = "pvtu"

# verify that two files are of same file type
if first_file[-4:] != second_file[-4:]:
    print("Fidelity test failed: Mismatched file types")
    quit()

# read in tolerance value
user_tolerance = input("Enter desired comparison tolerance value (default = 1e-12): ")
if float(user_tolerance) != CONST_TOLERANCE:
    CONST_TOLERANCE = float(user_tolerance)

# read files 
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
    print("Fidelity test failed: Mismatched data array count", "\n", "File 1:", point_data1.GetNumberOfArrays(), 
                                                               "\n", "File 2:", point_data2.GetNumberOfArrays())
    quit()

for i in range(point_data1.GetNumberOfArrays()):
    arr1 = point_data1.GetArray(i)
    arr2 = point_data2.GetArray(i)

    # verify both files contain same arrays
    if point_data1.GetArrayName(i) != point_data2.GetArrayName(i):
        print("Fidelity test failed: Mismatched data array names", "\n", "File 1:", point_data1.GetArrayName(i), 
                                                                   "\n", "File 2:", point_data2.GetArrayName(i))
        quit()

    # verify arrays are same sizes in both files
    if arr1.GetSize() != arr2.GetSize():
        print("Fidelity test failed: Mismatched data array sizes", "\n", "File 1, DataArray", i, ":", arr1.GetSize(), 
                                                                   "\n", "File 2, DataArray", i, ":", arr2.GetSize())
        quit()

    # verity individual values w/in given tolerance
    for j in range(arr1.GetSize()):
        if (arr1.GetValue(j) - arr2.GetValue(j)) > CONST_TOLERANCE: 
            print("Fidelity test failed: Mismatched data array values with tolerance", CONST_TOLERANCE)
            quit()

print("Fidelity test completed successfully.")
