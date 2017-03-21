using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace IMDBUtils.Models
{
    public enum EDelimiters
    {
        None= 0,
        Comma,
        CurrencySymbols,
        DoubleSpace,
        CommaAndRoundBracket,
        Semicolon,
    }

    [Serializable]
    class Preset
    {
        public Preset()
        {
            UpgradeDelimitsVersion();
            nSelectedDelim = (int)EDelimiters.None;
        }

        public void UpgradeDelimitsVersion()
        {
            m_srcDelimits = new ObservableCollection<Delimeters>();
            srcDelimits.Clear();
            srcDelimits.Add(new Delimeters("None"));
            srcDelimits.Add(new Delimeters("Comma"));
            srcDelimits.Add(new Delimeters("Currency Symbols"));
            srcDelimits.Add(new Delimeters("Double Space"));
            srcDelimits.Add(new Delimeters("Comma + Parentheses"));
            srcDelimits.Add(new Delimeters("Semicolon"));

            // if the new verison has more delimeters than older version, just init as 0.
            if (nSelectedDelim > srcDelimits.Count)
            {
                nSelectedDelim = (int)EDelimiters.None;
            }
        }


        private int m_nSelectedDelim;
        public int nSelectedDelim
        {
            get { return m_nSelectedDelim; }
            set
            {
                m_nSelectedDelim = value;
            }
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

        //public bool isMaximumTextEnabled { get; set; }

    }
}
    