package com.mac.assistant

import android.os.Bundle
import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import com.mac.assistant.ui.theme.MACAssistantTheme
import com.mac.assistant.ui.screens.MainScreen
import com.mac.assistant.viewmodel.AssistantViewModel

class MainActivity : ComponentActivity() {
    
    private val assistantViewModel: AssistantViewModel by viewModels()
    
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            assistantViewModel.onPermissionGranted()
        } else {
            assistantViewModel.onPermissionDenied()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Check and request audio permission
        checkAudioPermission()
        
        setContent {
            MACAssistantTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainScreen(
                        viewModel = assistantViewModel,
                        onRequestPermission = { requestAudioPermission() }
                    )
                }
            }
        }
    }
    
    private fun checkAudioPermission() {
        when {
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) == PackageManager.PERMISSION_GRANTED -> {
                assistantViewModel.onPermissionGranted()
            }
            else -> {
                requestAudioPermission()
            }
        }
    }
    
    private fun requestAudioPermission() {
        requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
    }
}
