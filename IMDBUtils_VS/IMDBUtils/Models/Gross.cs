using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace IMDBUtils.Models
{
    class Gross
    {
        public Gross()
        {

        }
        public Gross(DateTime _releasedate, string _country, string _amount, string _else)
        {
            this.Releasedate = _releasedate;
            this.Country = _country;
            this.Amount = _amount;
            this.Else = _else;
        }

        public void SetReleaseDate(string _releasedate)
        {
            this.Releasedate= DateTime.Parse(_releasedate);
        }

        public string AsString()
        {
            string str = string.Empty;
            str += "Country : " + Country;
            str += " | Gross : " + Amount;
            str += " | Releasedate : " + Releasedate.ToShortDateString();
            str += " | Else : " + Else;
            return str;
        }

        public DateTime Releasedate { get; set; }
        public string Country { get; set; }
        public string Amount { get; set; }
        public string Else { get; set; }
    }
}
