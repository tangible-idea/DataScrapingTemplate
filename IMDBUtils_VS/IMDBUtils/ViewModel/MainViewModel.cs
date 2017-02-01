using GalaSoft.MvvmLight;
using GalaSoft.MvvmLight.Command;
using IMDBUtils.Models;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Windows;
using System.Windows.Input;

namespace IMDBUtils.ViewModel
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
    /// This class contains properties that the main View can data bind to.
    /// <para>
    /// Use the <strong>mvvminpc</strong> snippet to add bindable properties to this ViewModel.
    /// </para>
    /// <para>
    /// You can also use Blend to data bind with the tool's support.
    /// </para>
    /// <para>
    /// See http://www.galasoft.ch/mvvm
    /// </para>
    /// </summary>
    public class MainViewModel : ViewModelBase
    {

        public ObservableCollection<FileFormat> ExportSets { get; set; }
        //public ObservableCollection<Movie> Movies { get; set; }
        public ObservableCollection<FilePath> AcqList { get; set; }
        private ObservableCollection<Movie> m_movie;

        public ObservableCollection<Movie> Movies
        {
            get { return m_movie; }
            set
            {
                m_movie = value;
                RaisePropertyChanged("Movies");
            }
        }

        public ICommand LoadFiles { get; private set; }
        public ICommand ShowSheet { get; private set; }
        /// <summary>
        /// Initializes a new instance of the MainViewModel class.
        /// </summary>
        public MainViewModel()
        {
            ShowSheet = new RelayCommand(() => ShowSheetExecute(), () => true);
            LoadFiles = new RelayCommand(() => LoadFilesExecute(), () => true);

            AcqList = new ObservableCollection<FilePath>();
            ExportSets = new ObservableCollection<FileFormat>();
            ExportSets.Add(new FileFormat("TXT"));
            ExportSets.Add(new FileFormat("CSV"));
            ExportSets.Add(new FileFormat("XLS"));
            ExportSets.Add(new FileFormat("XLSX"));
        }

        private void ParseStringArray(ref List<string[]> arrStrings)
        {
            string line = string.Empty;

            //this.Dispatcher.Invoke(DispatcherPriority.Normal, new Action(delegate ()
            //{
            //    prgExport.Maximum = lstFiles.Items.Count;
            //}));

            foreach (FilePath existFN in AcqList)
            {
                // Read the file line by line.
                //EStatus = EMode.ReadDataFile;
                System.IO.StreamReader file = new System.IO.StreamReader(existFN.Title);
                while ((line = file.ReadLine()) != null)
                {
                    arrStrings.Add(line.Split('|'));
                }
                file.Close();
            }
        }

        private void LoadFilesExecute()
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
                    AcqList.Add(new FilePath(FN));
                }
            }
        }
        private void ShowSheetExecute()
        {
            List<string[]> strArrays = new List<string[]>();
            //EStatus = EMode.ReadDataFile;
            this.ParseStringArray(ref strArrays);

            //string[] currMovieStringArr = null;
            //this.Dispatcher.Invoke(new Action(delegate ()
            //{
            //currMovieStringArr = strArrays[lstFiles.SelectedIndex];
            //   prgPresent.Maximum = strArrays.Count;
            //}));

            var arrMovie = new ObservableCollection<Movie>();
            // splite string arrays
            for (int i = 0; i < strArrays.Count; ++i)
            {
                var currMovie = new Movie(strArrays[i]);
                arrMovie.Add(currMovie);
                //this.Dispatcher.Invoke(new Action(delegate ()
                //{
                //    prgPresent.Value = i;
                //}));
            }
            Movies = arrMovie;
            MessageBox.Show(Movies.Count+"");
        }

    }
}