
void testDayConvert(std::ofstream &harnessOutput)
{
    bool proper = false;
    std::string ret_val;
    std::string answers[] = {"1st", "2nd", "3rd", "4th", "5th", "6th", "7th",
                             "8th", "9th", "10th", "11th", "12th", "13th", 
                             "14th", "15th", "16th", "17th", "18th", "19th", 
                             "20th", "21st", "22nd", "23rd", "24th", "25th", 
                             "26th", "27th", "28th", "29th", "30th", "31st"};

    for (int i=1; i <= 31; i++)
    {
        std::stringstream strm;
        strm << i;
        std::string s = strm.str();
        try
        {
            ret_val = dayConvert(s);
            proper = answers[i-1] == ret_val;
            if (!proper)
            {
                harnessOutput << "Calling dayConvert(\"" + s + "\")";
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
            cerr << "Calling dayConvert(\"" + s + "\")";
            cerr << "\t";
            cerr << "Out of Range exception thrown by: ";
            cerr << oor.what() << endl;
            
        }
        catch(...)
        {
            cerr << "Exception thrown ";
            cerr << "calling dayConvert(\"" + s + "\")";
        }
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

    testDayConvert(harnessOutput);

    harnessOutput.close();
    return 0;
}
