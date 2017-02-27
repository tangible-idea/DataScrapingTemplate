using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace IMDBUtils.Models
{
    [Serializable]
    class Preset
    {
        public Preset()
        {
            m_srcDelimits = new ObservableCollection<Delimeters>();
            srcDelimits.Add(new Delimeters("None"));
            srcDelimits.Add(new Delimeters("Comma"));
            srcDelimits.Add(new Delimeters("Gross"));
        }

        private ObservableCollection<Delimeters> m_srcDelimits;
        public ObservableCollection<Delimeters> srcDelimits
        {
            get { return m_srcDelimits; }
            set { m_srcDelimits = value; }
        }

        private string m_strTitle;
        public string strTitle
        {
            get { return m_strTitle; }
            set { m_strTitle = value; }
        }


        private string m_strMaximum;
        public string strMaximum
        {
            get { return m_strMaximum; }
            set { m_strMaximum = value; }
        }

    }
}
    