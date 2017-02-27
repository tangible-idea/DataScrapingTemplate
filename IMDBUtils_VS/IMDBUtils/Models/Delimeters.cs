using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace IMDBUtils.Models
{
    [Serializable]
    class Delimeters
    {
        public Delimeters(string _strDelim)
        {
            this.strDelimiter = _strDelim;
        }
        public override string ToString()
        {
            return strDelimiter;
        }
        public string strDelimiter { get; set; }
    }
}
