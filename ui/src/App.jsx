import {createContext, useMemo, useState} from 'react'
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import {createTheme, CssBaseline, ThemeProvider} from "@mui/material";
import TheTable from "./TheTable.jsx";

export const ColorModeContext = createContext({
    toggleColorMode: () => {}
})

const getColorMode = () => JSON.parse(localStorage.getItem('darkMode')) ? 'dark' : 'light'
const setDarkMode = value => localStorage.setItem('darkMode', JSON.stringify(value))

const App = () => {
    const [mode, setMode] = useState(getColorMode())
    const colorMode = useMemo(
        () => ({
            toggleColorMode: () => {
                setMode((prevMode) => {
                    const newMode = prevMode === 'light' ? 'dark' : 'light'
                    setDarkMode(newMode === 'dark')
                    return newMode
                })
            },
        }),
        [],
    );

    // Update the theme only if the mode changes
    const theme = useMemo(
        () =>
            createTheme({
                palette: {
                    mode,
                },
            }),
        [mode],
    )

    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline/>
                <TheTable/>
            </ThemeProvider>
        </ColorModeContext.Provider>
    )
}

export default App
