import {useCallback, useContext, useEffect, useState} from 'react'

import {Alert, Box, Button, Snackbar, useTheme} from "@mui/material";
import {DataGrid, GridToolbar} from "@mui/x-data-grid";
import {gridColumns} from "./gridOptions";
import MaterialUISwitch from "./SwitchButton.jsx";
import {ColorModeContext} from "./App.jsx";
import {apiPath, districts as availableDistricts} from "./constants.js";


const fetchFlats = async () => {
    const resp = await fetch(apiPath + '/flats/')
    return await resp.json()
}

const updateFlats = async (districts) => {
    const resp = await fetch(apiPath + '/flats/', {
        method: 'POST',
        headers: {'content-type': 'application/json'},
        body: districts && JSON.stringify(districts)
    })
    return await resp.json()
}

const defaultColumnVisibility = {
    id: false,
}

const CustomToolbar = ({refetch, isLoading}) => {
    const colorMode = useContext(ColorModeContext)
    const theme = useTheme()

    return (
        <Box display={"flex"} justifyContent={"space-between"} px={1}>
            <GridToolbar/>
            <Box display={"flex"} gap={2}>
                <Button onClick={refetch} disabled={isLoading}>Refresh</Button>
                <MaterialUISwitch onClick={colorMode.toggleColorMode} checked={theme.palette.mode === 'dark'}/>
            </Box>

        </Box>
    )
}

const TheTable = () => {
    const [isLoading, setIsLoading] = useState(true)
    const [flatList, setFlatList] = useState([])
    const [columnVisibilityModel, setColumnVisibilityModel] = useState(JSON.parse(localStorage.getItem('columnVisibilityModel')) || defaultColumnVisibility)
    const refetchFlats = useCallback(async () => {
        setIsLoading(true)
        const rows = await fetchFlats()
        setFlatList(rows)
        setIsLoading(false)
    }, [])

    useEffect(() => {
        refetchFlats()
    }, [refetchFlats])

    const updateVisibilityModel = (value, reason) => {
        localStorage.setItem('columnVisibilityModel', JSON.stringify(value))
        setColumnVisibilityModel(value)
    }

    const [snackState, setSnackState] = useState({
        open: false,
        message: '',
        vertical: 'top',
        horizontal: 'center',
        severity: 'info'
    })
    const handleRefresh = useCallback(async () => {
        setIsLoading(true)
        const resp = await updateFlats(availableDistricts)
        if (resp) {
            await refetchFlats()
            setSnackState(prevState => ({
                ...prevState,
                open: true,
                severity: 'info',
                message: Object.entries(resp)
            }))

        } else {
            setSnackState(prevState => ({
                ...prevState,
                open: true,
                severity: 'error',
                message: 'Update error'
            }))
        }
        setIsLoading(false)
    }, [refetchFlats])

    const handleCloseSnack = (event, reason) => {
        if (reason === 'clickaway') {
            return
        }
        setSnackState(prevState => ({
            ...prevState,
            open: false,
            message: ''
        }))
    };


    return (
        <Box sx={{height: '100%'}}>
            <DataGrid
                loading={isLoading}
                rows={flatList}
                columns={gridColumns}
                slots={{
                    toolbar: props => <CustomToolbar refetch={handleRefresh} isLoading={isLoading}/>,
                }}
                initialState={{
                    columns: {
                        columnVisibilityModel: defaultColumnVisibility,
                    },
                }}
                columnVisibilityModel={columnVisibilityModel}
                onColumnVisibilityModelChange={updateVisibilityModel}
            />
            <Snackbar
                open={snackState.open}
                autoHideDuration={13000}
                onClose={handleCloseSnack}
                anchorOrigin={{vertical: snackState.vertical, horizontal: snackState.horizontal}}
            >
                <Alert
                    onClose={handleCloseSnack}
                    severity={snackState.severity}
                    variant="filled"
                    sx={{width: '100%'}}
                >
                    {Array.isArray(snackState.message) ? snackState.message.map(([k, v]) => {
                        if (v === null) {
                            return <div key={k}>{k}: too early to update</div>
                        }
                        return <div key={k}>{k}: +{v} new flats</div>
                    }) : snackState.message}
                </Alert>
            </Snackbar>
        </Box>
    )
}

export default TheTable
