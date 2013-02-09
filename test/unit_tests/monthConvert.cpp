void testMonthConvert(std::ofstream &harnessOutput)
{
    std::string answers[] = {"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"};
    std::string invalid = "Invalid Month";

    for (int i=1; i <= 12; i++)
    {
        std::stringstream strm;
        strm << i;
        std::string s = strm.str();
        if (answers[i-1] != monthConvert(s))
        {
            harnessOutput.width(40);
            harnessOutput << "Calling monthConvert(\"" + s + "\")";

            harnessOutput.width(17);
            harnessOutput << "Expected Result: ";

            harnessOutput.width(20);
            harnessOutput << answers[i-1];

            harnessOutput.width(10);
            harnessOutput << "Received: ";
            
            harnessOutput.width(20);
            harnessOutput << monthConvert(s) << std::endl;
        }
    }
    std::string s = "0";
    if (invalid != monthConvert(s))
    {
        harnessOutput.width(40);
        harnessOutput << "Calling monthConvert(\"" + s + "\")";

        harnessOutput.width(17);
        harnessOutput << "Expected Result: ";

        harnessOutput.width(20);
        harnessOutput << invalid;
        
        harnessOutput.width(10);
        harnessOutput << "Received: ";

        harnessOutput.width(20);
        harnessOutput << monthConvert(s) << std::endl;
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
