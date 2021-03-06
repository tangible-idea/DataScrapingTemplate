﻿using Parse;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace IMDBUtils.Models
{
    public class Task
    {
        CultureInfo provider = CultureInfo.InvariantCulture;
        string format = "yyyy-MM-dd HH:mm:ss.ffffff";

        public Task()
        {

        }

        public string Name { get; set; }
        public string Range { get; set; }
        public string RangeEnd { get; set; }

        private string m_status;
        public string Status    // (string) pending, working, done
        {
            get { return m_status; }
            set
            {
                if (value != null)
                {
                    Status2 = value.Equals("working");
                    IsDownloadable = value.Equals("done");  // done : is downloadable
                }
                m_status = value;
            }
        }


        private bool m_Status2;

        public bool Status2// (bool) working : true.
        {
            get { return m_Status2; }
            set
            {
                m_Status2 = value;
            }
        }

        public double Progress { get; set; }
        public double ProgressMax { get; set; }
        public string rawDataURI { get; set; }
        public string Progress_server { get; set; }
        public string LastPage { get; set; }
        public string ProgressCaption { get; set; }

        private DateTime m_dtStartedAt;
        private string m_StartedAt;
        public string StartedAt
        {
            get { return m_StartedAt; }
            set
            {
                if (!value.Equals(string.Empty))
                {
                    m_dtStartedAt = DateTime.ParseExact(value, format, provider);
                    // TODO : unify all timezone to UTC
                    //var EasternTimeNow= TimeZoneInfo.ConvertTimeBySystemTimeZoneId(DateTime.Now
                    //    , "Eastern Standard Time"
                    //    , "Korea Standard Time");
                    //var duration = EasternTimeNow.Subtract(m_dtStartedAt);

                    //TimeSpent = String.Format("{0:dd}day {0:hh}h{0:mm}m{0:ss}s", duration);
                }
                
                m_StartedAt = value;
            }
        }

        private DateTime m_dtFinishedAt;
        private string m_FinishedAt;
        public string FinishedAt
        {
            get { return m_FinishedAt; }
            set
            {
                if (!value.Equals(string.Empty))
                {
                    m_dtFinishedAt = DateTime.ParseExact(value, format, provider);
                    var duration = m_dtFinishedAt.Subtract(m_dtStartedAt);
                    TimeSpent = String.Format("{0:hh}h{0:mm}m{0:ss}s", duration);
                    lfTimeSpentPerTask = duration.TotalSeconds / this.ProgressMax;
                    TimeSpentPerTask = String.Format("{0:F3}secs", lfTimeSpentPerTask);
                }
                m_FinishedAt = value;
            }
        }

        public string TimeSpent { get; set; }
        public string TimeSpentPerTask { get; set; }
        public double lfTimeSpentPerTask { get; set; }
        public bool IsDownloadable { get; set; }

        public string strErrPage { get; set; }
        public string strErrIdx { get; set; }

        public ParseObject PO { get; set; }
    }
}
