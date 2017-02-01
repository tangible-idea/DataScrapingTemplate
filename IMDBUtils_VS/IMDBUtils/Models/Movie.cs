using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace IMDBUtils.Models
{
    public class Movie
    {
        public Movie()
        {

        }

        public Movie(string[] arr)
        {
            try
            {
                this.Title = arr[0];
                this.URL = arr[1];
                this.Director = arr[2];
                this.Writers = arr[3];
                this.Stars = arr[4];
                this.Nominations = arr[5];
                this.Reviews = arr[6];
                this.Critics = arr[7];
                this.Popularity = arr[8];
                this.MetaScore = arr[9];
                this.Genre = arr[10];
                this.Rating = arr[11];
                this.Country = arr[12];
                this.Langs = arr[13];
                this.Budget_outside = arr[14];
                this.Release_date = arr[15];
                this.Opening_Weekend_outside = arr[16];
                this.Gross_outside = arr[17];
                this.Budget_detail = arr[18];
                this.Opening_weekind_detail = arr[19];
                this.Gross_detail = arr[20];
                this.World_Gross_detail = arr[21];
                this.Adminissions_detail = arr[22];
                this.Rentals_detail = arr[23];
                this.Fliming_dates_detail = arr[24];
                this.Copyright_detail = arr[25];
                this.Production_company = arr[26];
                this.Distributors = arr[27];
                this.Runtime_detail = arr[28];
                this.Color = arr[29];
                this.Flim_length = arr[30];
                this.Rating_value = arr[31];
                this.Rating_count = arr[32];
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }
        public string Title { get; set; }
        public string URL { get; set; }
        public string Director { get; set; }
        public string Writers { get; set; }
        public string Stars { get; set; }
        public string Nominations { get; set; }
        public string Reviews { get; set; }
        public string Critics { get; set; }
        public string Popularity { get; set; }
        public string MetaScore { get; set; }
        public string Genre { get; set; }
        public string Rating { get; set; }
        public string Country { get; set; }
        public string Langs { get; set; }
        public string Budget_outside { get; set; }
        public string Release_date { get; set; }
        public string Opening_Weekend_outside { get; set; }
        public string Gross_outside { get; set; }
        public string Budget_detail { get; set; }
        public string Opening_weekind_detail { get; set; }
        public string Gross_detail { get; set; }
        public string World_Gross_detail { get; set; }
        public string Adminissions_detail { get; set; }
        public string Rentals_detail { get; set; }
        public string Fliming_dates_detail { get; set; }
        public string Copyright_detail { get; set; }
        public string Production_company { get; set; }
        public string Distributors { get; set; }
        public string Runtime_detail { get; set; }
        public string Color { get; set; }
        public string Flim_length { get; set; }
        public string Rating_value { get; set; }
        public string Rating_count { get; set; }
    }
}