void testMonthConvert(std::ofstream &harnessOutput)
{
    bool proper = false;
    std::string ret_val;

    std::string answers[] = {"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"};
    std::string invalid = "Invalid Month";

    for (int i=1; i <= 12; i++)
    {
        std::stringstream strm;
        strm << i;
        std::string s = strm.str();
        try
        {
            cout << "Calling monthConvert(\"" + s + "\")" << endl;
            ret_val = monthConvert(s);
            proper = answers[i-1] == ret_val;
            if (!proper)
            {
                harnessOutput << "Calling monthConvert(\"" + s + "\")";
                harnessOutput << "\t";

                harnessOutput << "Expected Result: ";
                harnessOutput << answers[i-1];
                harnessOutput << "\t";

                harnessOutput << "Received: ";
                harnessOutput << ret_val << std::endl;
            }
        }
        catch(out_of_range& oor)
        {
            cerr << "Calling monthConvert(\"" + s + "\")";
            cerr << "\t";
            cerr << "Out of Range exception thrown by: ";
            cerr << oor.what() << endl;
            
        }
        catch(...)
        {
            cerr << "Calling monthConvert(\"" + s + "\")";
            cerr << "\t";
            cerr << "exception thrown" << endl;
        }
    }
    std::string s = "0";
    try
    {
        cout << "Calling monthConvert(\"" + s + "\")" << endl;
        ret_val = monthConvert(s);
        proper = invalid == ret_val;
        if (!proper)
        {
            harnessOutput << "Calling monthConvert(\"" + s + "\")";
            harnessOutput << "\t";

            harnessOutput << "Expected Result: ";
            harnessOutput << invalid;
            harnessOutput << "\t";
            
            harnessOutput << "Received: ";
            harnessOutput << ret_val << std::endl;
        }
    }
    catch(out_of_range& oor)
    {
        cerr << "Calling monthConvert(\"" + s + "\")";
        cerr << "\t";
        cerr << "Out of Range exception thrown by: ";
        cerr << oor.what() << endl;
        
    }
    catch(...)
    {
        cerr << "Calling monthConvert(\"" + s + "\")";
        cerr << "\t";
        cerr << "exception thrown" << endl;
    }
}


int main(int argc, char **argv)
{
    std::string function_to_test;
    std::ofstream harnessOutput;
    if (argc > 1)
    {
        harnessOutput.open(argv[1]);
    }
    else 
    {
        std::cerr << "Incorrect number of command line arguments" << std::endl;
        return 1;
    }

    harnessOutput << std::left;

    testMonthConvert(harnessOutput);

    harnessOutput.close();
    return 0;
}
