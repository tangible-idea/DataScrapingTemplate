using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace IMDBUtils.Models
{
    public class Task
    {
        public Task()
        {

        }
        public string Name { get; set; }
        public string Range { get; set; }
        public string RangeEnd { get; set; }

        private string m_status;
        public string Status
        {
            get { return m_status; }
            set
            {
                if(value != null)
                    Status2 = value.Equals("working");
                m_status = value;
            }
        }


        public bool Status2 { get; set; }
        public double Progress { get; set; }
        public double ProgressMax { get; set; }
        public string rawDataURI { get; set; }
        public string Progress_server { get; set; }
        public string LastPage { get; set; }
        public string StartedAt { get; set; }
        public string FinishedAt { get; set; }
        public string ProgressCaption { get; set; }
    }
}
