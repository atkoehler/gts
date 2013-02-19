/// @file unit_tests/main.cpp
/// @brief provide a main function for the unit test harness
/// 
///         takes 2 or 3 command line arguments:
///             1st is output file for unit test case failure results
///             2nd is output file for unit test errors
///             3rd is input file utilized if tested function takes input
///                 input file is optional command line arg
///         You shouldn't have to edit this file at all
int main(int argc, char **argv)
{
    std::string function_to_test;
    std::ofstream harnessOutput;
    std::ofstream harnessError;
    if(argc == 3 || argc == 4)
    {
        harnessOutput.open(argv[1]);
        harnessError.open(argv[2]);
    }
    else 
    {
        cerr << "Incorrect number of command line args" << std::endl;
        return 1;
    }

    if (argc == 4)
        testFunction(harnessOutput, harnessError, argv[3]);        
    else
        testFunction(harnessOutput, harnessError);
    
    harnessOutput.close();
    harnessError.close();
    return 0;
}
