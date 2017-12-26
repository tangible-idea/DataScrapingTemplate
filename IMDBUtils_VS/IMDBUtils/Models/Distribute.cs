using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace IMDBUtils.Models
{
    public class Distribute : IExcelData
    {
        public string distribute { get; set; }

        public Distribute(string _distribute)
        {
            this.distribute = _distribute;
        }
        // from interface
        public string AsString()
        {
            return distribute;
        }
    }
}
