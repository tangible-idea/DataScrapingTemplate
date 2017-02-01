using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace IMDBUtils.Models
{
    public class FilePath
    {
        public FilePath(string _title)
        {
            m_strTitle = _title;
        }
        private string m_strTitle;
        public string Title
        {
            get { return m_strTitle; }
            set
            {
                if (value == m_strTitle) return;
                m_strTitle = value;
            }
        }
    }
}
