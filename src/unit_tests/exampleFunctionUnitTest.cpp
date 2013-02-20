/// @file unit_tests/exampleFunctionUnitTest.cpp
/// @brief unit test function for function that implements getNewGuess logic
///
///         You should read the README and update the TODOs in this file.
///         And the file name should be same name as function, for example
///         testing the function absValue the name would be absValue.cpp. If
///         the function name is abs_value then the file is abs_value.cpp.
///
/// @param harnessOutput is a reference to an opened file for harness results
/// @param harnessError is a reference to an opened file for harness errors
/// @param input is the location of the input file that will be utilized
///         this is an optional parameter and if not specified will be NULL
///
void testFunction(std::ofstream &harnessOutput, std::ofstream &harnessError, 
                  char *input = NULL)
{
    bool proper = false;

    // TODO: update return value type to be of expected type
    std::string ret_val;
    std::ofstream inputFile;
    
    // TODO: Answers that are expected, only one char expected at a time
    std::string ansA[] = {"July 4th, 1776",
                          "November 1st, 2012"};
    vector <std::string> ans(ansA, ansA + sizeof(ansA) / sizeof(ansA[0]));

    // TODO: Parameters to provide function -- one vector per parameter
    std::string parA[] = {"7/4/1776",
                          "11/1/12"};
    vector <std::string> par(parA, parA + sizeof(parA) / sizeof(parA[0]));

    // Create input file if warranted 
    // Single test case's input per line, cin.ignore '\n' utilized after test
    vector <std::string> input_contents;
    if (input != NULL)
    {
        // TODO: input file contents can always go out as strings
        input_contents.push_back("e");    

        // extra inputs should change depending on what sort of valid inputs
        // are to be expected by the program
        std::string extra = "a b c d e f g h i j k l m n o p q " +
                            "r s t u v w x y z";

        // clear the file before writing, write out input and extra per line
        inputFile.open(input, ios::out | ios::trunc);
        for (int i = 0; i < input_contents.size(); i++)    
        {
            inputFile << input_contents.at(i) << " " << extra << std::endl 
                << std::endl;
        }
        inputFile.close(); 
    }       

    // go through every test in the unit test (each test has 1 answer)
    for (int i=0; i < ans.size(); i++)
    {
        // TODO: section title for output, script should replace the generic name
        std::string call = "Calling STUDENT_FUNC_NAME(\"" +  par.at(i) + "\")";

        try
        {
            // output the section title to standard output so it precedes
            // any function output within standard out for this individual test
            std::cout << call << std::endl;

            // TODO: call to generic function, script should replace the name
            ret_val = STUDENT_FUNC_NAME(par.at(i));

            // determine if the return value is what is expected
            proper = ans.at(i) == ret_val;
            if (!proper)
            {
                // tab separation utilized to break up title and items that 
                // should exist in a list below the title

                // output section title to harness output
                harnessOutput << call;
                harnessOutput << "\t";

                // output what was expected
                harnessOutput << "Expected Result: ";
                harnessOutput << ans.at(i);
                harnessOutput << "\t";

                // output what was returned by the function call
                harnessOutput << "Received: ";
                harnessOutput << ret_val;
                
                // output the input file contents for this test if warranted
                if (input != NULL)
                {
                    harnessOutput << "\t";
                    harnessOutput << "Input File Conents: ";
                    harnessOutput << input_contents.at(i);
                }
                harnessOutput << std::endl;
            }
        }
        catch(out_of_range& oor)
        {
            // Catch out of range errors, output section title and what threw
            // the exception separated by a tab, similar to harnessOutput
            harnessError << call;
            harnessError << "\t";
            harnessError << "Out of Range exception thrown by: ";
            harnessError << oor.what() << std::endl;
            
        }
        catch(...)
        {
            // Catch all other exceptions, output section title and a simple
            // statement that an exception was thrown
            harnessError << call;
            harnessError << "\t";
            harnessError << "exception thrown" << std::endl;
        }

        // The next test's input will be after the next newline
        if (input != NULL)
        {
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        }
    }
}

