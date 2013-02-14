void testDateConvert(std::ofstream &harnessOutput)
{
    bool proper = false;
    std::string ret_val;
    std::string queries[] = {"7/4/1776", "12/7/1941", "2/2/1929", "9/11/2001",
                             "1/23/45", "1/15/17", "10/30/1998", "11/1/12"};
    std::string answers[] = {"July 4th, 1776",
                             "December 7th, 1941",
                             "February 2nd, 1929",
                             "September 11th, 2001",
                             "January 23rd, 2045",
                             "January 15th, 2017",
                             "October 30th, 1998",
                             "November 1st, 2012"};

    for (int i=0; i < 8; i++)
    {
        try
        {
            ret_val = dateConvert(queries[i]);
            proper = answers[i] == ret_val;
            if (!proper)
            {
                harnessOutput << "Calling dateConvert(\"" + queries[i] + "\")";
                harnessOutput << "\t";
                
                harnessOutput << "Expected Result: ";
                harnessOutput << answers[i];
                harnessOutput << "\t";

                harnessOutput << "Received: ";
                harnessOutput << ret_val << std::endl;
            }
        }
        catch(out_of_range& oor)
        {
            cerr << "Calling dateConvert(\"" + queries[i] + "\")";
            cerr << "\t";
            cerr << "Out of Range exception thrown by: ";
            cerr << oor.what() << endl;
            
        }
        catch(...)
        {
            cerr << "Calling dateConvert(\"" + queries[i] + "\")";
            cerr << "\t";
            cerr << "exception thrown" << endl;
        }
    }
}


int main(int argc, char **argv)
{
    std::string function_to_test;
    std::ofstream harnessOutput;
    if (argc != 1)
    {
        harnessOutput.open(argv[1]);
    }
    else 
    {
        std::cerr << "Incorrect number of command line arguments" << std::endl;
        return 1;
    }

    harnessOutput << std::left;

    testDateConvert(harnessOutput);

    harnessOutput.close();
    return 0;
}
