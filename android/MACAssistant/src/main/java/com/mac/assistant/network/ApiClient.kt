package com.mac.assistant.network

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import java.util.concurrent.TimeUnit

object ApiClient {
    
    private var retrofit: Retrofit? = null
    
    fun getClient(baseUrl: String): ApiService {
        if (retrofit?.baseUrl().toString() != baseUrl) {
            val logging = HttpLoggingInterceptor()
            logging.setLevel(HttpLoggingInterceptor.Level.BODY)
            
            val client = OkHttpClient.Builder()
                .addInterceptor(logging)
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build()
            
            retrofit = Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
        }
        
        return retrofit!!.create(ApiService::class.java)
    }
    
    fun formatUrl(serverUrl: String): String {
        var url = serverUrl.trim()
        
        // Add http:// if no protocol specified
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            url = "http://$url"
        }
        
        // Add default port if no port specified
        if (!url.contains(":8000") && !url.contains(":80") && !url.contains(":443")) {
            val parts = url.split("://")
            if (parts.size == 2) {
                val protocol = parts[0]
                val host = parts[1].trimEnd('/')
                url = "$protocol://$host:8000"
            }
        }
        
        // Ensure URL ends with /
        if (!url.endsWith("/")) {
            url += "/"
        }
        
        return url
    }
}
