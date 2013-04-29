/// @file unit_tests/main.cpp
/// @brief unit test function for function that implements main logic
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

string convertInt(int number)
{
   stringstream ss;
   ss << number;
   return ss.str();
}

void testFunction(std::ofstream &harnessOutput, std::ofstream &harnessError, 
                  char *input = NULL)
{
    bool proper = false;

    // update return value type to be of expected type
    int ret_val;
    std::ofstream inputFile;
    
    // Answers that are expected, only one char expected at a time
    int ansA[] = {0};
    vector <int> ans(ansA, ansA + sizeof(ansA) / sizeof(ansA[0]));

    // Parameters to provide function -- one vector per parameter
    std::string parA[] = {"empty"};
    vector <std::string> par(parA, parA + sizeof(parA) / sizeof(parA[0]));

    // Create input file if warranted 
    // Single test case's input per line, cin.ignore '\n' utilized after test
    vector <std::string> input_contents;
    if (input != NULL)
    {
        // input file contents can always go out as strings
        input_contents.push_back("Kris Pinhead N a b E W W");    

        // extra inputs should change depending on what sort of valid inputs
        // are to be expected by the program
        std::string extra = "W W W W W W W W W W W W";

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
        // section title for output, script should replace the generic name
        std::string call = "Calling STUDENT_FUNC_NAME()";

        try
        {
            // output the section title to standard output so it precedes
            // any function output within standard out for this individual test
            std::cout << call << std::endl;

            // call to generic function, script should replace the name
            ret_val = STUDENT_FUNC_NAME();

            // determine if the return value is what is expected
            proper = ret_val == 0; 
            if (!proper)
            {
                // tab separation utilized to break up title and items that 
                // should exist in a list below the title

                // output section title to harness output
                harnessOutput << call;
                harnessOutput << "\t";

                // output what was expected
                harnessOutput << "Expected Result: ";
                harnessOutput << ans.at(0);
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

