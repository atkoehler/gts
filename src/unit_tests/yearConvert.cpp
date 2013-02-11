void testYearConvert(std::ofstream &harnessOutput)
{
    bool proper = false;
    std::string ret_val;
    std::string answers[] = {"1945", "2043", "1900", "2000", "1979"};

    for (int i=0; i < 5; i++)
    {
        std::string s = answers[i];

        if (s.substr(0,2) == "20")
        {
            std::string n = s.substr(2,2);
            try
            {
                ret_val = yearConvert(n);
                proper = answers[i] == ret_val;
                if (!proper)
                {
                    harnessOutput << "Calling yearConvert(\"" + n + "\")";
                    harnessOutput << "\t";

                    harnessOutput << "Expected Result: ";
                    harnessOutput << answers[i];
                    harnessOutput << "\t";
                    
                    harnessOutput << "Received: ";
                    harnessOutput << yearConvert(n) << std::endl;
                }
            } 
            catch(...)
            {
                cerr << "Exception thrown ";
                cerr << "calling yearConvert(\"" + n + "\")";
            }
        }
                
        try
        {
            ret_val = yearConvert(s);
            proper = answers[i] == ret_val;
            if (!proper)
            {
                harnessOutput << "Calling yearConvert(\"" + s + "\")";
                harnessOutput << "\t";

                harnessOutput << "Expected Result: ";
                harnessOutput << answers[i];
                harnessOutput << "\t";
                
                harnessOutput << "Received: ";
                harnessOutput << yearConvert(s) << std::endl;
            }
        }
        catch(...)
        {
            cerr << "Exception thrown ";
            cerr << "calling yearConvert(\"" + s + "\")";
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

    testYearConvert(harnessOutput);
    
    harnessOutput.close();
    return 0;
}
