void testYearConvert(std::ofstream &harnessOutput)
{
    std::string answers[] = {"1945", "2043", "1900", "2000", "1979"};

    for (int i=0; i < 5; i++)
    {
        std::string s = answers[i];

        if (s.substr(0,2) == "20")
        {
            std::string n = s.substr(2,2);
            if (answers[i] != yearConvert(n))
            {
                harnessOutput.width(40);
                harnessOutput << "Calling yearConvert(\"" + n + "\")";

                harnessOutput.width(17);
                harnessOutput << "Expected Result: ";
                
                harnessOutput.width(10);
                harnessOutput << answers[i];
                
                harnessOutput.width(10);
                harnessOutput << "Received: ";
                
                harnessOutput.width(10);
                harnessOutput << yearConvert(n) << std::endl;
            }
        }
                
        if (answers[i] != yearConvert(s))
        {
            harnessOutput.width(40);
            harnessOutput << "Calling yearConvert(\"" + s + "\")";

            harnessOutput.width(17);
            harnessOutput << "Expected Result: ";
            
            harnessOutput.width(10);
            harnessOutput << answers[i];
            
            harnessOutput.width(10);
            harnessOutput << "Received: ";
            
            harnessOutput.width(10);
            harnessOutput << yearConvert(s) << std::endl;
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
