using IMDBUtils.Models;
using IMDBUtils.ViewModel;
using MahApps.Metro.Controls;
using MahApps.Metro.Controls.Dialogs;
using Parse;
using SmartXLS;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Formatters.Binary;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.Windows.Threading;

namespace IMDBUtils
{
    public enum EMode
    {
        None = 0,
        Idle = 1,
        OpeningFile = 2,
        ReadDataFile = 3,
        WritingFile = 4,
        ClosingFile = 5
    }


    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : MetroWindow
    {
        private EMode m_eWorking;
        public EMode EStatus
        {
            get { return m_eWorking; }
            set
            {
                this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
                {
                    switch (value)
                    {
                        case EMode.Idle:
                            btnExportToXLS.Content = "Export to XLS";
                            btnExportToXLS.IsEnabled = true;
                            btnLoad.IsEnabled = true;
                            break;
                        case EMode.OpeningFile:
                            btnExportToXLS.Content = "Creating...";
                            btnExportToXLS.IsEnabled = false;
                            btnLoad.IsEnabled = false;
                            break;
                        case EMode.ReadDataFile:
                            btnExportToXLS.Content = "Reading...";
                            btnExportToXLS.IsEnabled = false;
                            btnLoad.IsEnabled = false;
                            break;
                        case EMode.WritingFile:
                            btnExportToXLS.Content = "Writing...";
                            btnExportToXLS.IsEnabled = false;
                            btnLoad.IsEnabled = false;
                            break;
                        case EMode.ClosingFile:
                            btnExportToXLS.Content = "Saving...";
                            btnExportToXLS.IsEnabled = false;
                            btnLoad.IsEnabled = false;
                            break;
                    }
                }));

                m_eWorking = value;
            }
        }
        private static string strSelectedFile = string.Empty;
        ObservableCollection<Gross> lstGross = new ObservableCollection<Gross>();
        ObservableCollection<Models.Task> TaskList= new ObservableCollection<Models.Task>();
        ObservableCollection<Models.Task> TaskErrList = new ObservableCollection<Models.Task>();

        ObservableCollection<Preset> m_PresetList = new ObservableCollection<Preset>();
        ObservableCollection<Preset> PresetList
        {
            get { return m_PresetList; }
            set
            {
                m_PresetList = value;
            }
        }


        public MainWindow()
        {
            InitializeComponent();

        }


        private void MetroWindow_Loaded(object sender, RoutedEventArgs e)
        {
            var a = new Preset();
            a.strTitle = "Name";
            a.strMaximum = "0";
            PresetList.Add(a);
            lstPreset.ItemsSource = PresetList;
        }
        private void btnLoad_Click(object sender, RoutedEventArgs e)
        {
            // Create OpenFileDialog 
            Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();

            // Set filter for file extension and default file extension 
            dlg.DefaultExt = ".txt";
            dlg.Filter = "TEXT Files (*.txt)|*.txt";
            dlg.Multiselect = true;

            // Display OpenFileDialog by calling ShowDialog method 
            Nullable<bool> result = dlg.ShowDialog();

            // Get the selected file name and display in a TextBox 
            if (result == true)
            {
                foreach (var FN in dlg.FileNames)
                {
                    //var onlyFN = System.IO.Path.GetFileName(FN);
                    lstFiles.Items.Add(FN);
                    #region validation
                    //if(lstFiles.Items.Count == 0)
                    //{
                    //    lstFiles.Items.Add(onlyFN);
                    //}
                    //else
                    //{
                    //    foreach (string existFN in lstFiles.Items)
                    //    {
                    //        if(existFN.Equals(onlyFN) == false)
                    //        {
                    //            lstFiles.Items.Add(onlyFN);
                    //        }
                    //    }

                    //}
                    #endregion
                }
            }
        }

        private readonly BackgroundWorker worker = new BackgroundWorker();

        private void btnExportToXLS_Click(object sender, RoutedEventArgs e)
        {
            worker.DoWork += Do_ExportWork;
            worker.RunWorkerCompleted += Done_ExportWork;

            EStatus = EMode.OpeningFile;
            worker.RunWorkerAsync();
        }

        private void ParseStringArray(ref List<string[]> arrStrings)
        {
            string line = string.Empty;

            this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
            {
                prgExport.Maximum = lstFiles.Items.Count;
            }));

            foreach (FilePath existFN in lstFiles.Items)
            {
                // Read the file line by line.
                EStatus = EMode.ReadDataFile;
                System.IO.StreamReader file = new System.IO.StreamReader(existFN.Title);
                while ((line = file.ReadLine()) != null)
                {
                    arrStrings.Add(line.Split('|'));
                }
                file.Close();
            }
        }

        /// <summary>
        /// being in export
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Do_ExportWork(object sender, DoWorkEventArgs e)
        {
            int nRes = 0;
            int nFileCounter = 0;
            List<string[]> arrStrings = new List<string[]>();

            this.ParseStringArray(ref arrStrings);

            this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
            {
                lstFiles.SelectedIndex = nFileCounter;
            }));

            var path= lstFiles.Items[nFileCounter] as FilePath;
            var strCurrName = System.IO.Path.GetFileNameWithoutExtension(path.Title);
            var strCurrPath = System.IO.Path.GetDirectoryName(path.Title);

            EStatus = EMode.WritingFile;
            nRes = AddToWorkbook(strCurrPath + "\\" + strCurrName + ".xlsx", arrStrings);
            if (nRes == -1)
            {
                MessageBox.Show("error!");
            }
            else
            {
                this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
                {
                    prgExport.Value = ++nFileCounter;
                }));
            }

        }

        /// <summary>
        /// When export is done
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Done_ExportWork(object sender, RunWorkerCompletedEventArgs e)
        {
            worker.DoWork -= Do_ExportWork;
            worker.RunWorkerCompleted -= Done_ExportWork;
            //update ui once worker complete his work
            EStatus = EMode.Idle;
        }

        /// <summary>
        /// create or write data to xlsx file.
        /// </summary>
        /// <param name="strPath"></param>
        /// <param name="arrStrings"></param>
        /// <returns></returns>
        private int AddToWorkbook(string strPath, List<string[]> arrStrings)
        {
            this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
            {
                prgExport_Single.Value = 0;
            }));

            WorkBook m_book = new WorkBook();
            if (File.Exists(strPath) == true)    // if it already exists change into read mode.
            {
                File.Delete(strPath);
            }
            //int nRowOffset = 0;
            //WorkBook m_book = new WorkBook();
            //if (File.Exists(strPath) == true)    // if it already exists change into read mode.
            //{
            //    m_book.readXLSX(strPath);
            //    nRowOffset = m_book.LastRow;
            //}
            this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
            {
                prgExport_Single.Maximum = arrStrings.Count;
            }));


            int nMaxRow = 0;
            int nMaxCol = 0;

            try
            {
                m_book.setSheetName(0, "IMDB");
                m_book.Sheet = 0;

                for (int row = 0; row < arrStrings.Count; ++row)
                {
                    nMaxRow = Math.Max(nMaxRow, row);
                    this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
                    {
                        prgExport_Single.Value = row;
                    }));
                    for (int col = 0; col < arrStrings[row].Length; ++col)
                    {
                        int nSelDelim = PresetList[col].nSelectedDelim;
                        int nDelimMax = Convert.ToInt32(PresetList[col].strMaximum);
                        this.DelimitWithSelectedDelimiter(nSelDelim, nDelimMax, arrStrings[row][col]);

                        nMaxCol = Math.Max(nMaxCol, col);
                        m_book.setText(row/* + nRowOffset*/, col, arrStrings[row][col]);
                    }
                }

                #region Apply Style
                RangeStyle rangeStyle = m_book.getRangeStyle(0, 0, nMaxRow /*+ nRowOffset*/, nMaxCol);//get format from range B2:C3
                rangeStyle.FontName = "Arial";
                m_book.setRangeStyle(rangeStyle, 0, 0, nMaxRow /*+ nRowOffset*/, nMaxCol); //set format for range B2:C3
                #endregion

                //m_book.AutoRecalc = false;
                EStatus = EMode.ClosingFile;
                m_book.recalc();
                m_book.writeXLSX(strPath);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
                return -1;
            }
            finally
            {
                m_book = null;
                arrStrings = null;
            }

            return nMaxRow;
        }


        /// <summary>
        /// 
        /// </summary>
        /// <param name="nSelDelim"></param>
        /// <param name="nDelimMax"></param>
        /// <param name="strContent"></param>
        /// <returns></returns>
        private List<string> DelimitWithSelectedDelimiter(int nSelDelim, int nDelimMax, string strContent)
        {
            var arrRes = new List<string>();
            if (nSelDelim == (int)EDelimiters.None)
            {

            }
            else if (nSelDelim == (int)EDelimiters.Comma)
            {
                arrRes= strContent.Split(',').ToList();
            }
            else if (nSelDelim == (int)EDelimiters.CurrencySymbols)
            {
                this.SplitGrossText(strContent, false);
                foreach(var g in lstGross)
                {
                    arrRes.Add(g.AsString());
                }
            }
            else if (nSelDelim == (int)EDelimiters.DoubleSpace)
            {
                arrRes = strContent.Split(new[] { "  " }, StringSplitOptions.RemoveEmptyEntries).ToList();
            }
            return arrRes;
        }

        private void Do_ShowSheet(object sender, DoWorkEventArgs e)
        {
            List<string[]> strArrays = new List<string[]>();
            EStatus = EMode.ReadDataFile;
            this.ParseStringArray(ref strArrays);

            //string[] currMovieStringArr = null;
            this.Dispatcher.Invoke(new Action(delegate ()
            {
                //currMovieStringArr = strArrays[lstFiles.SelectedIndex];
                prgPresent.Maximum = strArrays.Count;
            }));

            List<Movie> arrMovie = new List<Movie>();
            // splite string arrays
            for (int i = 0; i < strArrays.Count; ++i)
            {
                var currMovie = new Movie(strArrays[i]);
                arrMovie.Add(currMovie);
                this.Dispatcher.Invoke(new Action(delegate ()
                {
                    prgPresent.Value = i;
                }));
            }


        }

        private void Done_ShowSheet(object sender, RunWorkerCompletedEventArgs e)
        {
            //MessageBox.Show("complete!");
            worker.DoWork -= Do_ShowSheet;
            worker.RunWorkerCompleted -= Done_ShowSheet;

            EStatus = EMode.Idle;
        }



        private void lstFiles_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            strSelectedFile = lstFiles.Items[lstFiles.SelectedIndex] as string;
            var onlyFN = System.IO.Path.GetFileName(strSelectedFile);
            btnLoadExcelData.Content = "Show data of " + onlyFN;
        }

        private void btnLoadExcelData_Click(object sender, RoutedEventArgs e)
        {
            worker.DoWork += Do_ShowSheet;
            worker.RunWorkerCompleted += Done_ShowSheet;
            worker.RunWorkerAsync();
            //MessageBox.Show(lstFiles.Items[lstFiles.SelectedIndex] as string);
        }

        private void btnSplit_Click(object sender, RoutedEventArgs e)
        {
            this.SplitGrossText(txtBefore.Text, true);
        }

        private void SplitGrossText(string strTarget, bool bViewing)
        {
            string strPattern = @"(\€|\$|\£| FRF | DEM | ARS)";
            List<string> substrings = Regex.Split(strTarget, strPattern).ToList();
            List<string> arrResult = new List<string>();
            string strSet = string.Empty;

            substrings.RemoveAt(0);
            for (int i = 0; i < substrings.Count; ++i)
            {
                if (i % 2 == 0)
                {
                    strSet = substrings[i];
                }
                else
                {
                    strSet += substrings[i];
                    arrResult.Add(strSet);
                }
            }
            
            lstGross.Clear();
            foreach (string str in arrResult)
            {
                try
                {
                    var gross = new Gross();
                    string[] arrGross = str.Split('(');
                    gross.Amount = arrGross[0].Replace(')', ' ').Trim();
                    gross.Country = arrGross[1].Replace(')', ' ').Trim();
                    gross.SetReleaseDate(arrGross[2].Replace(')', ' ').Trim());
                    gross.Else = arrGross[3].Replace(')', ' ').Trim();
                    lstGross.Add(gross);
                }
                catch (Exception ex)
                {
                }
            }

            if(bViewing)
            {
                this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
                {
                    dgAfter.ItemsSource = null;
                    dgAfter.ItemsSource = lstGross;
                }));
            }
            else
            {

            }
            
        }

        private void txtFilter_TextChanged(object sender, TextChangedEventArgs e)
        {
            var lstFilteredGross = FilterByCountry(txtFilter.Text);
                
            if (txtFilter.Text.Trim().Equals(""))
            {
                lstFilteredGross = lstGross;
            }

            //lstGross = lstFilteredGross;
            dgAfter.ItemsSource = null;
            dgAfter.ItemsSource = lstFilteredGross;
            dgAfter.Items.Refresh();

        }

        private ObservableCollection<Gross> FilterByCountry(string str)
        {
            var lstFilteredGross = new ObservableCollection<Gross>();
            foreach (Gross g in lstGross)
            {
                if (g.Country.Equals(str))
                {
                    lstFilteredGross.Add(g);
                }
            }
            return lstFilteredGross;
        }

        private List<Gross> FilterByReleaseDate(int nFirstN)
        {
            var lstFilteredGross = new List<Gross>();
            lstFilteredGross = lstGross.ToList();
            lstFilteredGross.Sort((x, y) => DateTime.Compare(x.Releasedate, y.Releasedate));
            lstFilteredGross = lstFilteredGross.Take(nFirstN).ToList();

            return lstFilteredGross;
        }

        private string strTargetAutomationFile = string.Empty;
        private void btnLoadForAuto_Click(object sender, RoutedEventArgs e)
        {
            // Create OpenFileDialog 
            Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();

            // Set filter for file extension and default file extension 
            dlg.DefaultExt = ".xlsx";
            dlg.Filter = "XLSX Files (*.xlsx)|*.xlsx";

            // Display OpenFileDialog by calling ShowDialog method 
            Nullable<bool> result = dlg.ShowDialog();

            // Get the selected file name and display in a TextBox 
            if (result == true)
            {
                strTargetAutomationFile= txtAutoFilePath.Text = dlg.FileName;
            }
        }

        private void btnRunForAuto_Click(object sender, RoutedEventArgs e)
        {
            worker.DoWork += Do_GrossAutomation;
            worker.RunWorkerCompleted += Done_GrossAutomation;
            worker.RunWorkerAsync();
        }

        private void Do_GrossAutomation(object sender, DoWorkEventArgs e)
        {
            var wbWrite = new WorkBook();
            wbWrite.setSheetName(0, "Gross");
            wbWrite.Sheet = 0;

            var wbRead = new WorkBook();
            if (File.Exists(strTargetAutomationFile) == true)    // if it already exists change into read mode.
            {
                wbRead.readXLSX(strTargetAutomationFile);
                this.Dispatcher.Invoke(new Action(delegate ()
                {
                    prgGrossAuto.Maximum = wbRead.LastRow;
                }));
            }
            else
            {
                MessageBox.Show("cannot find file.");
                return;
            }

            for(int row=0; row<wbRead.LastRow; ++row)
            {
                wbRead.Sheet = 0;
                string strGrossWorld= wbRead.getText(row, 1);

                if(strGrossWorld.Trim().Equals("") == false)
                {
                    SplitGrossText(strGrossWorld, false);
                    lstGross= this.FilterByCountry("USA");
                    var lstFiltered= this.FilterByReleaseDate(4);
                    for (int item=0; item< lstFiltered.Count; ++item)
                    {
                        wbWrite.setText(row, item, lstFiltered[item].AsString());
                        
                    }
                    this.Dispatcher.Invoke(new Action(delegate ()
                    {
                        lstGross.Clear();
                        prgGrossAuto.Value = row;
                    }));
                }
                else
                {
                    wbWrite.setText(row, 0, "null");
                }
            }
            
            wbWrite.writeXLSX(@".\\Gross.xlsx");
            MessageBox.Show("file was written");

        }

        private void Done_GrossAutomation(object sender, RunWorkerCompletedEventArgs e)
        {
            worker.DoWork -= Do_GrossAutomation;
            worker.RunWorkerCompleted -= Done_GrossAutomation;
        }

        public async void RefreshRemoteTable()
        {
            prgRing.IsActive = true;
            try
            {
                var query = ParseObject.GetQuery("Parsing_range");
                IEnumerable<ParseObject> lstParsingRange = await query.FindAsync();

                TaskList.Clear();
                int nCountTodo = 0;
                double lfTotalSpeed = 0.0f;
                int nCountDoneTasks = 0;
                int nCountWorkingServer = 0;
                foreach (var PO in lstParsingRange)
                {
                    var task = new Models.Task();
                    task.PO = PO;
                    task.Progress = Convert.ToDouble(PO["done_count"]);
                    task.ProgressMax = Convert.ToDouble(PO["quantity"]);
                    task.Range = PO["range"] as string;
                    task.RangeEnd = PO["range_end"] as string;
                    task.Status = PO["status"] as string;
                    task.Progress_server = Convert.ToString(Convert.ToDouble(PO["progress"]));

                    task.LastPage = PO["last_page"] as string;

                    if (task.LastPage.Equals(""))
                        task.LastPage = "about:blank";

                    task.StartedAt = PO["starting_time"] as string;
                    task.FinishedAt = PO["ending_time"] as string;

                    task.ProgressCaption = task.Progress + " / " + task.ProgressMax;

                    this.AnalTask(task, ref nCountTodo, ref lfTotalSpeed, ref nCountDoneTasks, ref nCountWorkingServer);

                    TaskList.Add(task);
                }

                TimeSpan tsEstimate = TimeSpan.FromSeconds(0);
                if(nCountWorkingServer != 0)
                {
                    double lfTotalEstimateTime = ((double)nCountTodo * (lfTotalSpeed / (double)nCountDoneTasks)) / (double)nCountWorkingServer;
                    tsEstimate = TimeSpan.FromSeconds(lfTotalEstimateTime);
                }
                string strDetails = String.Format("Remaining tasks : {0},\tAverage speed : {1:F3} movie/sec,\tTotal remaining : {2} (estimate)"
                    , nCountTodo, lfTotalSpeed / (double)nCountDoneTasks, String.Format("{0:dd}day(s) {0:hh}h{0:mm}m{0:ss}s", tsEstimate));
                txtDetails.Text = strDetails;
                lstWorks.ItemsSource = null;
                lstWorks.ItemsSource = TaskList;
                prgRing.IsActive = false;

            }
            catch (Exception ex)
            {
                MessageBox.Show("Got connection pbm\n" + ex.Message);
            }
        }

        private void AnalTask(Models.Task task, ref int nCount, ref double totalSpeed, ref int nCountDoneTasks, ref int nCountWorkingServer)
        {
            if(task.ProgressMax == 0)
            {
                nCount += 10000;    // estimation
            }
            else
            {
                nCount += ((int)task.ProgressMax - (int)task.Progress);
            }

            if (task.Status2)
                nCountWorkingServer++;

            if (task.TimeSpentPerTask == null)
                return;

            if(task.TimeSpentPerTask.Equals(string.Empty) == false)
            {
                ++nCountDoneTasks;
                totalSpeed += task.lfTimeSpentPerTask;
            }
        }

        public void TabControl_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.Source is TabControl)
            {
                if (TabRemote.IsSelected)
                    RefreshRemoteTable();
                else if(TabErrMonitor.IsSelected)
                    RefreshErrTable();
            }
        }

        private void Hyperlink_RequestNavigate(object sender, RequestNavigateEventArgs e)
        {
            Process.Start(new ProcessStartInfo(e.Uri.AbsoluteUri));
            e.Handled = true;
        }

        private void btnRefreshRemote_Click(object sender, RoutedEventArgs e)
        {
            RefreshRemoteTable();
        }


        private void btnRefreshErr_Click(object sender, RoutedEventArgs e)
        {
            RefreshErrTable();
        }

        private async void RefreshErrTable()
        {
            prgRingErr.IsActive = true;
            try
            {
                var query = ParseObject.GetQuery("Parsing_err").Limit(1000);
                IEnumerable<ParseObject> lstParsingRange = await query.FindAsync();

                TaskErrList.Clear();
                foreach (var PO in lstParsingRange)
                {
                    var task = new Models.Task();
                    task.PO = PO;
                    task.Progress = Convert.ToDouble(PO["done_count"]);
                    task.ProgressMax = 50 - Convert.ToInt32(PO["entity_num"]);
                    task.Status = PO["status"] as string;
                    task.strErrIdx = Convert.ToString(PO["entity_num"]);
                    task.strErrPage = Convert.ToString(PO["page_num"]);

                    task.LastPage = PO["err_url"] as string;
                    task.ProgressCaption = task.Progress + " / " + task.ProgressMax;

                    if (task.LastPage.Equals(""))
                        task.LastPage = "about:blank";

                    TaskErrList.Add(task);
                }

                lstWorks2.ItemsSource = null;
                lstWorks2.ItemsSource = TaskErrList;
                prgRingErr.IsActive = false;

            }
            catch (Exception ex)
            {
                MessageBox.Show("Got connection pbm\n" + ex.Message);
            }
        }

        private async void btnDownload_Click(object sender, RoutedEventArgs e)
        {
            string myPath = Environment.CurrentDirectory;
            Button button = sender as Button;
            var task = button.DataContext as Models.Task;

            if (button.Content.Equals("Open"))
            {
                Process.Start(myPath);
                return;
            }
            try
            {
                var rawFile = task.PO.Get<ParseFile>("rawdata");
                button.Content = "...";
                button.IsEnabled = false;
                string dataText = await new HttpClient().GetStringAsync(rawFile.Url);
                string onlyFN = System.IO.Path.GetFileName(rawFile.Url.ToString());

                using (StreamWriter outputFile = new StreamWriter(myPath + onlyFN))
                {
                    outputFile.Write(dataText);
                }

                button.Content = "Open";
                button.IsEnabled = true;
            }
            catch (Exception ex)
            {
                button.Content = "Error";
                button.Foreground = Brushes.Red;
                MessageBox.Show("Access denied\n" + ex.Message);
            }

        }
        private async void btnErase_Click(object sender, RoutedEventArgs e)
        {
            string myPath = Environment.CurrentDirectory;
            Button button = sender as Button;
            var task = button.DataContext as Models.Task;

            task.PO["status"] = "pending";
            task.PO["done_count"] = 0;
            await task.PO.SaveAsync();

            this.RefreshErrTable();
        }


        private void btnLoadConvertingPresetFile_Click(object sender, RoutedEventArgs e)
        {
            btnLoadPreset_Click(sender, e);
        }
        private async void btnLoadPreset_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();

                dlg.DefaultExt = ".imdbpreset";
                dlg.Filter = "IMDB Preset File (*.imdbpreset)|*.imdbpreset";

                Nullable<bool> result = dlg.ShowDialog();

                if (result == true)
                {
                    IFormatter formatter = new BinaryFormatter();
                    Stream stream = new FileStream(dlg.FileName, FileMode.Open, FileAccess.Read, FileShare.None);
                    if (stream.Length == 0)
                    {
                        await this.ShowMessageAsync("Abnormal file", "empty file.");
                        return;
                    }
                    PresetList.Clear();
                    PresetList = formatter.Deserialize(stream) as ObservableCollection<Preset>;
                    foreach(var p in PresetList)
                    {
                        p.UpgradeDelimitsVersion();
                    }
                    lstPreset.ItemsSource = PresetList;
                    lstPreset.Items.Refresh();
                    stream.Close();

                    txtConvertingPresetFile.Text = dlg.FileName;
                }
            }
            catch (Exception ex)
            {
                await this.ShowMessageAsync("Abnormal file", ex.Message);
            }
        }

        private async void btnSavePreset_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Microsoft.Win32.SaveFileDialog dlg = new Microsoft.Win32.SaveFileDialog();

                dlg.DefaultExt = ".imdbpreset";
                dlg.Filter = "IMDB Preset File (*.imdbpreset)|*.imdbpreset";

                Nullable<bool> result = dlg.ShowDialog();

                if (result == true)
                {
                    IFormatter formatter = new BinaryFormatter();
                    Stream stream = new FileStream(dlg.FileName, FileMode.Create, FileAccess.Write, FileShare.None);
                    formatter.Serialize(stream, PresetList);
                    stream.Close();
                }

            }
            catch (Exception ex)
            {
                await this.ShowMessageAsync("Failed to save file", ex.Message);
            }
        }

        private void ComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var comboBox = sender as ComboBox;
            Int32 itemIndex = lstPreset.Items.IndexOf(comboBox.DataContext);

            if (comboBox.SelectedIndex == -1)
                return;
        }

        private void btnPresetDelete_Click(object sender, RoutedEventArgs e)
        {
            var btn = sender as Button;
            Int32 itemIndex = lstPreset.Items.IndexOf(btn.DataContext);

            PresetList.RemoveAt(itemIndex);
        }

        private void btnPresetInsert_Click(object sender, RoutedEventArgs e)
        {
            var btn = sender as Button;
            Int32 itemIndex = lstPreset.Items.IndexOf(btn.DataContext);

            var p = new Preset();
            p.strMaximum = "0";
            p.nSelectedDelim = 0;
            PresetList.Insert(itemIndex + 1, p);
        }
        
    }
}
