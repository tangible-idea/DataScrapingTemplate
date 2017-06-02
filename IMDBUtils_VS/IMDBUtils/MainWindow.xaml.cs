using IMDBUtils.Models;
using MahApps.Metro.Controls;
using MahApps.Metro.Controls.Dialogs;
using NPOI.SS.UserModel;
using NPOI.XSSF.UserModel;
using Parse;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Formatters.Binary;
using System.Text.RegularExpressions;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Navigation;
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
                            btnExportToXLS.Content = "Export as XLS";
                            btnExportToXLS.IsEnabled = true;
                            btnLoad.IsEnabled = true;
                            btnLoadConvertingPresetFile.IsEnabled = true;
                            btnLoadPreset.IsEnabled = true;
                            lstPreset.IsEnabled = true;
                            break;
                        case EMode.OpeningFile:
                            btnExportToXLS.Content = "Creating...";
                            btnExportToXLS.IsEnabled = false;
                            btnLoad.IsEnabled = false;
                            btnLoadConvertingPresetFile.IsEnabled = false;
                            btnLoadPreset.IsEnabled = false;
                            lstPreset.IsEnabled = false;
                            break;
                        case EMode.ReadDataFile:
                            btnExportToXLS.Content = "Reading...";
                            btnExportToXLS.IsEnabled = false;
                            btnLoad.IsEnabled = false;
                            btnLoadConvertingPresetFile.IsEnabled = false;
                            btnLoadPreset.IsEnabled = false;
                            lstPreset.IsEnabled = false;
                            break;
                        case EMode.WritingFile:
                            btnExportToXLS.Content = "Writing...";
                            btnExportToXLS.IsEnabled = false;
                            btnLoad.IsEnabled = false;
                            btnLoadConvertingPresetFile.IsEnabled = false;
                            btnLoadPreset.IsEnabled = false;
                            lstPreset.IsEnabled = false;
                            break;
                        case EMode.ClosingFile:
                            btnExportToXLS.Content = "Saving...";
                            btnExportToXLS.IsEnabled = false;
                            btnLoad.IsEnabled = false;
                            btnLoadConvertingPresetFile.IsEnabled = false;
                            btnLoadPreset.IsEnabled = false;
                            lstPreset.IsEnabled = false;
                            break;
                    }
                }));

                m_eWorking = value;
            }
        }
        public bool m_bPresetLoaded = false;
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

        private async void btnExportToXLS_Click(object sender, RoutedEventArgs e)
        {
            if(lstFiles.Items.Count == 0)
            {
                await this.ShowMessageAsync("Error", "Please load at least one file.");
                return;
            }
            worker.DoWork += Do_ExportWork;
            worker.RunWorkerCompleted += Done_ExportWork;

            EStatus = EMode.OpeningFile;
            worker.RunWorkerAsync();
        }

        private void ParseStringArray(ref List<string[]> arrStrings, FilePath currPath)
        {
            string line = string.Empty;
            bool bAutomacTruncate = false;

            this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
            {
                prgExport.Maximum = lstFiles.Items.Count;
                bAutomacTruncate = (bool)chkAutoTruncate.IsChecked;
            }));
            

            // Read the file line by line.
            EStatus = EMode.ReadDataFile;
            System.IO.StreamReader file = new System.IO.StreamReader(currPath.Title);
            while ((line = file.ReadLine()) != null)
            {
                var arrSplited = line.Split('|');
                if (bAutomacTruncate == true)
                {
                    for(int i=0; i<arrSplited.ToList().Count; ++i)
                    {
                        if (arrSplited[i].Length > 32767)
                        {
                            Console.WriteLine("exceed the cell limit : " + arrSplited[i].Length);
                            String truncated = Utils.Utils.TruncateWithOutDot(arrSplited[i], 32767);
                            arrSplited[i] = (truncated);
                        }
                    }
                }
                arrStrings.Add(arrSplited);
            }
            file.Close();
        }

        /// <summary>
        /// being in export
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Do_ExportWork(object sender, DoWorkEventArgs e)
        {
            for(int i=0; i< lstFiles.Items.Count; ++i)
            {
                int nRes = 0;
                List<string[]> arrStrings = new List<string[]>();

                var path= lstFiles.Items[i] as FilePath;
                var strCurrName = System.IO.Path.GetFileNameWithoutExtension(path.Title);
                var strCurrPath = System.IO.Path.GetDirectoryName(path.Title);

                this.ParseStringArray(ref arrStrings, path);

                this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
                {
                    lstFiles.SelectedIndex = i;
                }));

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
                        prgExport.Value = i + 1;
                    }));
                }

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

            IWorkbook m_book = new XSSFWorkbook();
            if (File.Exists(strPath) == true)    // if it already exists change into read mode.
            {
                Console.WriteLine("This file alreay exist.");
                File.Delete(strPath);
                Console.WriteLine("Old file has deleted.");
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
                m_book.CreateSheet("IMDB");
                var currSheet = m_book.GetSheet("IMDB") as XSSFSheet;
                //m_book.setSheetName(0, "IMDB");
                //m_book.Sheet = 0;

                for (int row = 0; row < arrStrings.Count; ++row)
                {
                    nMaxRow = Math.Max(nMaxRow, row);
                    this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
                    {
                        prgExport_Single.Value = row;
                    }));

                    IRow _row= currSheet.CreateRow(row);
                    int nShift = 0;
                    for (int col = 0; col < arrStrings[row].Length; ++col)
                    {
                        // without preset file
                        if (m_bPresetLoaded == false)
                        {
                            
                            {
                                _row.CreateCell(col).SetCellValue(arrStrings[row][col]);
                            }
                            //Console.WriteLine("length : " + arrStrings[row][col].Length);
                            //m_book.setText(row/* + nRowOffset*/, col, arrStrings[row][col]);
                        }
                        else    // converting with preset 
                        {
                            if(row == 0)
                            {
                                this.MakeHeaders(ref currSheet, nShift);
                                continue;
                            }
                            int nSelDelim = PresetList[col].nSelectedDelim;
                            int nDelimMax = Convert.ToInt32(PresetList[col].strMaximum);

                            var arrDelimitedString = new List<string>();
                            if (nSelDelim == (int)EDelimiters.None)
                            {
                                _row.CreateCell(col + nShift).SetCellValue(arrStrings[row][col]);
                                //m_book.setText(row/* + nRowOffset*/, col+ nShift, arrStrings[row][col]);
                            }
                            else
                            {
                                arrDelimitedString = this.DelimitWithSelectedDelimiter(nSelDelim, nDelimMax, arrStrings[row][col]);

                                if (arrDelimitedString.Count != 0)
                                {
                                    for (int s = 0; s < nDelimMax; s++)
                                    {
                                        if (arrDelimitedString.Count <= s)
                                            break;

                                        _row.CreateCell(col + s + nShift).SetCellValue(arrDelimitedString[s]);
                                        //m_book.setText(row, col+s+nShift, arrDelimitedString[s]);
                                        //string joined = string.Join(" / ", arrDelimitedString.ToArray());
                                        //m_book.setText(row, col, joined);
                                    }
                                }
                                nShift += nDelimMax - 1;
                            }
                        }
                        nMaxCol = Math.Max(nMaxCol, col+ nShift);
                    }
                }

                #region Apply Style
                //RangeStyle rangeStyle = m_book.getRangeStyle(0, 0, nMaxRow /*+ nRowOffset*/, nMaxCol);//get format from range B2:C3
                //rangeStyle.FontName = "Arial";
                //m_book.setRangeStyle(rangeStyle, 0, 0, nMaxRow /*+ nRowOffset*/, nMaxCol); //set format for range B2:C3
                #endregion

                //m_book.AutoRecalc = false;
                EStatus = EMode.ClosingFile;

                FileStream sw = File.Create(strPath);
                m_book.Write(sw);
                sw.Close();

                Console.WriteLine("All done. file path : "+strPath);
                //m_book.recalc();
                //m_book.writeXLSX(strPath);
            }
            catch (Exception ex)
            {
                //if (bErrorIgnored)
                {
                    MessageBox.Show(ex.Message);
                    return -1;
                }
            }
            finally
            {
                m_book = null;
                arrStrings = null;
            }

            return nMaxRow;
        }

        
        private void MakeHeaders(ref XSSFSheet book, int nShift)
        {
            IRow _row= book.CreateRow(0);
            for (int header_col = 0; header_col < PresetList.Count; ++header_col)
            {
                int nHeaderDelimMax = Convert.ToInt32(PresetList[header_col].strMaximum);
                int nHeaderSelDelim = PresetList[header_col].nSelectedDelim;
                if ((nHeaderSelDelim != (int)EDelimiters.None)
                    && (nHeaderDelimMax != 0))
                {
                    for (int s = 0; s < nHeaderDelimMax; s++)
                    {
                        _row.CreateCell(header_col + nShift + s).SetCellValue(PresetList[header_col].strTitle + (s + 1));
                        //book.setText(0, header_col + nShift + s, PresetList[header_col].strTitle + (s + 1));
                    }
                    nShift += nHeaderDelimMax - 1;
                }
                else
                {
                    _row.CreateCell(header_col + nShift).SetCellValue(PresetList[header_col].strTitle);
                    //book.setText(0, header_col + nShift, PresetList[header_col].strTitle);
                }
            }
            Console.WriteLine("done to add headers.");
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
            if (nSelDelim == (int)EDelimiters.Comma)
            {
                arrRes = strContent.Split(new[] { "," }, StringSplitOptions.RemoveEmptyEntries).ToList();
            }
            else if (nSelDelim == (int)EDelimiters.CurrencySymbols)
            {
                this.SplitGrossText(strContent, false);
                foreach (var g in lstGross)
                {
                    arrRes.Add(g.AsString());
                }
            }
            else if (nSelDelim == (int)EDelimiters.SingleSpace)
            {
                arrRes = strContent.Split(new[] { " " }, StringSplitOptions.RemoveEmptyEntries).ToList();
            }
            else if (nSelDelim == (int)EDelimiters.DoubleSpace)
            {
                arrRes = strContent.Split(new string[] { "  " }, StringSplitOptions.RemoveEmptyEntries).ToList();
            }
            else if (nSelDelim == (int)EDelimiters.CommaAndRoundBracket)
            {
                
                arrRes = strContent.Split(new char[] { ',', '(', ')' }, StringSplitOptions.RemoveEmptyEntries).ToList();
            }
            else if (nSelDelim == (int)EDelimiters.Semicolon)
            {
                arrRes = strContent.Split(new[] { ";" }, StringSplitOptions.RemoveEmptyEntries).ToList();
            }
            else if (nSelDelim == (int)EDelimiters.RoundBracket)
            {
                arrRes = strContent.Split(new string[] { "(", ")" }, StringSplitOptions.RemoveEmptyEntries).ToList();

            }
            else if (nSelDelim == (int)EDelimiters.Colon)
            {
                arrRes = strContent.Split(new[] { ":" }, StringSplitOptions.RemoveEmptyEntries).ToList();
            }
            return arrRes;
        }

        private void Do_ShowSheet(object sender, DoWorkEventArgs e)
        {
            List<string[]> strArrays = new List<string[]>();
            EStatus = EMode.ReadDataFile;
            this.ParseStringArray(ref strArrays, null);

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

        private List<string> SplitDistributeText(string strTarget)
        {
            List<string> res = new List<string>();
            List<string> ListOfDistribute = strTarget.Split('|').ToList();

            foreach(string Distribute in ListOfDistribute)
            {
                if (Distribute.Trim().Equals(""))
                    continue;

                bool bNeccessary = false;
                var ListSplited = Distribute.Split(new string[] { "(", ")" }, StringSplitOptions.RemoveEmptyEntries).ToList();
                var foundUSA = ListSplited.SingleOrDefault(x => x.Equals("USA"));
                var foundTheatrical = ListSplited.SingleOrDefault(x => x.Equals("theatrical"));
                var foundAllMedia = ListSplited.SingleOrDefault(x => x.Equals("all media"));

                if(foundUSA != null && foundTheatrical != null)
                {
                    bNeccessary = true;
                }
                else if (foundUSA != null && foundAllMedia != null)
                {
                    bNeccessary = true;
                }
                else if (foundTheatrical == null && foundUSA == null && foundAllMedia != null)
                {
                    bNeccessary = true;
                }

                if(bNeccessary)
                {
                    res.Add(Distribute);
                }
            }
            return res;

        }

        private void SplitGrossText(string strTarget, bool bViewing)
        {
            string strPattern = @"(\€|\$|\£| FRF | DEM | ARS | ESP | ITL | FIM | SEK | HKD | NLG | RUR)";
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

                    if(arrGross.Length >= 4)
                    {
                        gross.Amount = arrGross[0].Replace(')', ' ').Trim();
                        gross.Country = arrGross[1].Replace(')', ' ').Trim();
                        gross.SetReleaseDate(arrGross[2].Replace(')', ' ').Trim());
                        gross.Else = arrGross[3].Replace(')', ' ').Trim();
                        lstGross.Add(gross);
                    }
                    else if (arrGross.Length == 2)
                    {
                        gross.Amount = arrGross[0].Replace(')', ' ').Trim();
                        gross.Else = arrGross[1].Replace(')', ' ').Trim();
                        lstGross.Add(gross);
                    }
                    else if (arrGross.Length == 1)
                    {
                        gross.Amount = arrGross[0].Replace(')', ' ').Trim();
                        lstGross.Add(gross);
                    }
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
            IWorkbook wbWrite = new XSSFWorkbook();
            var shWrite = wbWrite.CreateSheet("Gross") as XSSFSheet;
            
            //var wbWrite = new WorkBook();
            //wbWrite.setSheetName(0, "Gross");
            //wbWrite.Sheet = 0;

            IWorkbook wbRead = null;
            XSSFSheet shRead = null;
            //var wbRead = new WorkBook();
            if (File.Exists(strTargetAutomationFile) == true)    // if it already exists, change into read mode.
            {
                wbRead= new XSSFWorkbook(strTargetAutomationFile);
                //wbRead.readXLSX(strTargetAutomationFile);
                shRead = wbRead.GetSheetAt(0) as XSSFSheet;
                this.Dispatcher.Invoke(new Action(delegate ()
                {
                    prgGrossAuto.Maximum = shRead.LastRowNum;
                }));
            }
            else
            {
                MessageBox.Show("cannot find file.");
                return;
            }

            //for(int row=0; row<wbRead.LastRow; ++row)
            for (int row = 0; row < shRead.LastRowNum; ++row)
            {
                string strTargetWord = string.Empty;
                if (bAlreadyDelimited)  // if data is already delimited
                {
                    var listOfCell = shRead.GetRow(row).ToList();
                    foreach (var cell in listOfCell)
                    {   // combine all contents of this row into one string
                        strTargetWord += cell.StringCellValue + "|";
                    }
                }
                else
                {
                    var Cell = shRead.GetRow(row).GetCell(NumberOfColumnForSpliting);
                    if (Cell == null)
                        continue;

                    strTargetWord = Cell.StringCellValue;
                }

                IRow _row= shWrite.CreateRow(row);
                if (strTargetWord.Trim().Equals("") == false)
                {
                    SplitDistributeText(strTargetWord);
                    //SplitGrossText(strTargetWord, false);
                    lstGross= this.FilterByCountry("USA");
                    var lstFiltered= this.FilterByReleaseDate(4);
                    for (int item=0; item< lstFiltered.Count; ++item)
                    {
                        _row.CreateCell(item).SetCellValue(lstFiltered[item].AsString());
                    }
                    this.Dispatcher.Invoke(new Action(delegate ()
                    {
                        lstGross.Clear();
                        prgGrossAuto.Value = row;
                    }));
                }
                else
                {
                    _row.CreateCell(0).SetCellValue("null");
                    //wbWrite.setText(row, 0, "null");
                }
            }


            //wbWrite.writeXLSX(@".\\Gross.xlsx");
            FileStream sw = File.Create(@".\\Gross.xlsx");
            wbWrite.Write(sw);
            sw.Close();
            MessageBox.Show("file has written");

        }


        public int NumberOfColumnForSpliting { get; set; }
        private void txtColumnNumber_TextChanged(object sender, TextChangedEventArgs e)
        {
            NumberOfColumnForSpliting= Convert.ToInt32((sender as TextBox).Text);
        }

        public bool bAlreadyDelimited { get; set; }
        private void chkAlreadyDelimited_Checked(object sender, RoutedEventArgs e)
        {
            bAlreadyDelimited = (bool)(sender as CheckBox).IsChecked;
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
                    m_bPresetLoaded = true;
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
            PresetList.Insert(itemIndex, p);
        }

        private void btnOpenPath_Conv_Click(object sender, RoutedEventArgs e)
        {
            if (lstFiles.Items.Count == 0)
                return;

            var path= lstFiles.Items[lstFiles.SelectedIndex] as FilePath;
            var strCurrPath = System.IO.Path.GetDirectoryName(path.Title);

            // opens the folder in explorer
            Process.Start(strCurrPath);
        }

    }
}
