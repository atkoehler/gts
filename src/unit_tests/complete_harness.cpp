
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
            harnessOutput << "Calling monthConvert(\"" + s + "\")";
            harnessOutput << "\t";

            harnessOutput << "Expected Result: ";
            harnessOutput << answers[i-1];
            harnessOutput << "\t";

            harnessOutput << "Received: ";
            harnessOutput << monthConvert(s) << std::endl;
        }
    }
    std::string s = "0";
    if (invalid != monthConvert(s))
    {
        harnessOutput << "Calling monthConvert(\"" + s + "\")";
        harnessOutput << "\t";

        harnessOutput << "Expected Result: ";
        harnessOutput << invalid;
        harnessOutput << "\t";
        
        harnessOutput << "Received: ";
        harnessOutput << monthConvert(s) << std::endl;
    }
}

void testDayConvert(std::ofstream &harnessOutput)
{
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
        if (answers[i-1] != dayConvert(s))
        {
            harnessOutput << "Calling dayConvert(\"" + s + "\")";
            harnessOutput << "\t";

            harnessOutput << "Expected Result: ";
            harnessOutput << answers[i-1];
            harnessOutput << "\t";
            
            harnessOutput << "Received: ";
            harnessOutput << dayConvert(s) << std::endl;
        }
    }
}

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
                harnessOutput << "Calling yearConvert(\"" + n + "\")";
                harnessOutput << "\t";

                harnessOutput << "Expected Result: ";
                harnessOutput << answers[i];
                harnessOutput << "\t";
                
                harnessOutput << "Received: ";
                harnessOutput << yearConvert(n) << std::endl;
            }
        }
                
        if (answers[i] != yearConvert(s))
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
}

void testDateConvert(std::ofstream &harnessOutput)
{
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
        if (answers[i] != dateConvert(queries[i]))
        {
            harnessOutput << "Calling dateConvert(\"" + queries[i] + "\")";
            harnessOutput << "\t";
            
            harnessOutput << "Expected Result: ";
            harnessOutput << answers[i];
            harnessOutput << "\t";

            harnessOutput << "Received: ";
            harnessOutput << dateConvert(queries[i]) << std::endl;
        }
    }
}

int main(int argc, char **argv)
{
    std::string function_to_test;
    std::ofstream harnessOutput;
    if (argc > 2)
    {
        function_to_test = argv[1];
        harnessOutput.open(argv[2]);
    }
    else 
    {
        std::cerr << "Incorrect number of command line arguments" << std::endl;
        return 1;
    }

    harnessOutput << std::left;

    if (function_to_test == "monthConvert")
    {
        testMonthConvert(harnessOutput);
    }
    else if(function_to_test == "dayConvert")
    {
        testDayConvert(harnessOutput);
    }
    else if(function_to_test == "yearConvert")
    {
        testYearConvert(harnessOutput);
    }
    else if(function_to_test == "dateConvert")
    {
        testDateConvert(harnessOutput);
    }

    harnessOutput.close();
    return 0;
}
