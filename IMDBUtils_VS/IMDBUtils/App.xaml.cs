using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using Parse;

namespace IMDBUtils
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        public App()
        {
            this.InitializeComponent();
            //this.Suspending += OnSuspending;

            ParseClient.Initialize(new ParseClient.Configuration
            {
                ApplicationId = "kj1rWYVT3D4u3hFE050P9u1GV6VSPUg7rPhB3VTK",
                WindowsKey = "CMwKxa8AAz9CZwIXNPwar6W1VrMT3PTmFSL5g6hP",
                Server = "https://pg-app-ld9iqyzik9lwgsdbx74gcbez5zkjh5.scalabl.cloud/1/"


                //ApplicationId = "vh60sQDbtfnIlFxn5HrK6oBj5SN1rqYeqtixIngY",
                //WindowsKey = "nhCNL1dnGWyWeZhnYx1m8HQ02pEU0B1xmIrNDu0Q",
                //Server = "https://parseapi.back4app.com/"

            });

        }
    }
}
